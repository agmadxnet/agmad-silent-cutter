#!/usr/bin/env python3
"""Local media processing. No shell evaluation or installation during daily runs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
PRESETS = {
    '1': ('8%', '0.20s', '0.45s,0.15s', 'LECTURE'),
    '2': ('12%', '0.12s', '0.25s,0.12s', 'SHORTS'),
    '3': ('20%', '0.06s', '0.15s,0.08s', 'AGGRESSIVE'),
    '4': ('30%', '0.04s', '0.10s,0.06s', 'VERY_AGGRESSIVE'),
    '5': ('40%', '0.02s', '0.08s,0.05s', 'MAXIMUM_TEST'),
}
MODEL = 'UVR-MDX-NET-Inst_HQ_3.onnx'
EXTENSIONS = {'.mp4', '.mov', '.mkv', '.m4v', '.webm', '.avi'}


def run(args, log):
    log.write('COMMAND: ' + repr([str(a) for a in args]) + '\n')
    log.flush()
    subprocess.run([str(a) for a in args], check=True, stdout=log, stderr=subprocess.STDOUT)


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)
    ]))


def fingerprint(path):
    h = hashlib.sha256()
    with open(path, 'rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def cleaned_source(source, mode, temp, log, notify):
    info = probe(source)
    video = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    audio = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    if not video or not audio:
        raise ValueError('Cleanup requires video and an audio track.')
    # Reject unusual stream offsets rather than silently shifting speech against the picture.
    offset = abs(float(video.get('start_time', 0)) - float(audio.get('start_time', 0)))
    if offset > 0.05:
        raise ValueError('Audio/video start offset exceeds 50ms. Normalize this recording before cleanup, or choose Off.')
    duration = float(audio.get('duration') or info['format']['duration'])
    engine = ROOT / 'tools' / 'runtime' / 'deep-filter'
    model = ROOT / 'tools' / 'models' / MODEL
    signature = fingerprint(engine if mode == 'noise' else model)
    key = hashlib.sha256((fingerprint(source) + mode + signature + 'v4.1-first-audio-48k-mono-delay-compensated').encode()).hexdigest()
    cache = ROOT / 'CACHE' / (key + '.wav')
    if cache.exists():
        try:
            cached = probe(cache)
            if abs(float(cached['format']['duration']) - duration) > 0.1:
                raise ValueError('Invalid cached duration')
            notify('Using cached cleaned audio.')
        except Exception:
            cache.unlink()
    if not cache.exists():
        extracted = temp / 'source.wav'
        run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', source, '-map', '0:a:0',
             '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s16le', extracted], log)
        separated = temp / 'separated'
        separated.mkdir()
        if mode == 'noise':
            notify('Removing noise locally...')
            run([engine, '--compensate-delay', '--output-dir', separated, extracted], log)
        else:
            notify('Separating voice from music locally (this can take time)...')
            python = ROOT / 'tools' / 'music-env' / 'bin' / 'python'
            run([python, ROOT / 'tools' / 'music.py', 'separate', extracted, separated], log)
        candidates = list(separated.glob('*.wav'))
        if len(candidates) != 1:
            raise ValueError('Cleanup must return exactly one voice WAV; inspect the log.')
        raw = candidates[0]
        actual = float(probe(raw)['format']['duration'])
        if abs(actual - duration) > 0.1:
            raise ValueError('Cleanup changed audio duration by more than 100ms; refusing potentially unsynchronized output.')
        # Correct small sample-rounding differences only; no stretching or automatic gain boost.
        normalized = temp / 'cleaned.wav'
        run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', raw,
             '-af', 'apad', '-t', str(duration), '-ar', '48000', '-ac', '1',
             '-c:a', 'pcm_s16le', normalized], log)
        # Publish complete cache entries atomically, even if two runs overlap.
        fd, staging = tempfile.mkstemp(prefix=key, suffix='.partial', dir=ROOT / 'CACHE')
        os.close(fd)
        try:
            shutil.copyfile(normalized, staging)
            os.replace(staging, cache)
        finally:
            if os.path.exists(staging):
                os.unlink(staging)
    prepared = temp / 'prepared.mkv'
    # Matroska accepts copied AV1/VP9 as well as H.264 with lossless FLAC audio.
    # MOV rejects AV1 at header writing, even when a re-encoded test excerpt succeeds.
    # Stream-copy picture: the final Auto-Editor render is the only video encoding pass.
    # Input timestamps are rebased together; only the cleaned first audio track is retained.
    run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', source, '-i', cache,
         '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'flac',
         '-map_metadata', '-1', prepared], log)
    return prepared


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in PRESETS or sys.argv[2] not in {'off', 'noise', 'music'}:
        print('Usage: process.py 1|2|3|4|5 off|noise|music')
        return 1
    strength, mode = sys.argv[1:]
    threshold, margin, smooth, tag = PRESETS[strength]
    for name in ('INPUT', 'OUTPUT', 'LOGS', 'CACHE'):
        (ROOT / name).mkdir(exist_ok=True)
    for tool in ('auto-editor', 'ffmpeg', 'ffprobe'):
        if not shutil.which(tool):
            print('Missing ' + tool + '. Run Setup_Local_Audio.command once.')
            return 1
    if mode == 'noise' and not os.access(ROOT / 'tools/runtime/deep-filter', os.X_OK):
        print('Noise engine missing. Run Setup_Local_Audio.command once, or choose Off.')
        return 1
    if mode == 'music' and not ((ROOT / 'tools/music-env/bin/python').exists() and (ROOT / 'tools/models' / MODEL).exists()):
        print('Music engine/model missing. Run Setup_Local_Audio.command once, or choose Off.')
        return 1
    files = sorted(p for p in (ROOT / 'INPUT').iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS)
    if not files:
        print('No supported video files in INPUT.')
        return 0
    run_dir = Path(tempfile.mkdtemp(prefix=time.strftime('run_%Y%m%d_%H%M%S_'), dir=ROOT / 'LOGS'))
    out = ROOT / 'OUTPUT' / run_dir.name
    out.mkdir()
    successes = failures = 0
    version = subprocess.check_output(['auto-editor', '--version'], text=True).strip()
    with open(run_dir / 'SUMMARY.txt', 'w') as summary:
        def notify(message):
            print(message, flush=True)
            summary.write(message + '\n')
            summary.flush()
        notify(f'Auto-Editor {version} | preset={strength} {tag} | cleanup={mode}')
        notify(f'threshold={threshold}, margin={margin}, smooth={smooth}')
        for index, source in enumerate(files, 1):
            target = out / f'{index:03d}_{source.stem}_{tag}_{mode.upper()}_CLEAN.mp4'
            logpath = run_dir / f'{index:03d}.log'
            notify('\nProcessing: ' + source.name)
            try:
                with open(logpath, 'w') as log, tempfile.TemporaryDirectory(prefix='processing_', dir=run_dir) as tmp:
                    ready = source if mode == 'off' else cleaned_source(source, mode, Path(tmp), log, notify)
                    args = ['auto-editor', ready, '--edit', f'audio:threshold={threshold}',
                            '--margin', margin, '--smooth', smooth, '--no-open']
                    stats = subprocess.run([str(a) for a in args] + ['--preview'], text=True,
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    log.write(stats.stdout)
                    log.flush()
                    notify(stats.stdout)
                    stats.check_returncode()
                    notify('Rendering video...')
                    run(args + ['--video-codec', 'libx264', '--audio-codec', 'aac', '--pix-fmt', 'yuv420p', '-o', target], log)
                    rendered = probe(target)
                    kinds = {s['codec_type'] for s in rendered['streams']}
                    if not {'audio', 'video'}.issubset(kinds) or float(rendered['format']['duration']) <= 0:
                        raise ValueError('Output verification failed.')
                notify('DONE: ' + str(target))
                successes += 1
            except Exception as exc:
                target.unlink(missing_ok=True)
                notify(f'FAILED: {source.name}: {exc}\nSee {logpath}')
                failures += 1
        notify(f'\nSuccessful: {successes} | Failed: {failures}\nReport: {run_dir / "SUMMARY.txt"}')
    return int(failures > 0)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Interrupted. Inspect the current output folder for partial files before use.')
        sys.exit(130)
