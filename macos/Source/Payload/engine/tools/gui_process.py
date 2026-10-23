#!/usr/bin/env python3
"""GUI adapter: the validated v4 cleanup/presets remain in process.py."""
import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import process as engine
from cut_settings import resolve


def emit(event, **fields):
    print(json.dumps(dict(event=event, **fields)), flush=True)


def cancelled(signum, frame):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    os.killpg(os.getpgrp(), signal.SIGTERM)
    raise KeyboardInterrupt()


def mapping(timeline, source_offset):
    rate = float(Fraction(timeline['timebase']))
    clips = timeline['v'][0]
    if rate <= 0 or not clips:
        raise ValueError('No video clips remain with these settings. Try a lower strength.')
    return [dict(start=float(c['start']) / rate, duration=float(c['dur']) / rate,
                 source=float(c['offset']) / rate + source_offset) for c in clips]


def render(ready, options, target, log, cut_off=False):
    if cut_off:
        engine.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', ready,
                    '-map', '0:v:0', '-map', '0:a:0', '-c:v', 'libx264', '-preset', 'fast',
                    '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', target], log)
    else:
        engine.run(options + ['--video-codec', 'libx264', '--audio-codec', 'aac',
                   '--pix-fmt', 'yuv420p', '-o', target], log)


def main():
    if os.getpgrp() != os.getpid():
        os.setsid()  # cancellation targets only this job and its children
    signal.signal(signal.SIGTERM, cancelled)
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--destination', required=True)
    ap.add_argument('--engine', required=True)
    ap.add_argument('--strength', choices=engine.PRESETS, default='3')
    ap.add_argument('--profile', choices=['scale','custom','gentle','standard'], default='scale')
    ap.add_argument('--level', type=int, choices=range(-5,6), default=0)
    ap.add_argument('--gentle-preset', choices=['1','2','3'], default='2')
    ap.add_argument('--threshold', type=float)
    ap.add_argument('--padding', type=float)
    ap.add_argument('--pause', type=float)
    ap.add_argument('--mode', choices=['off', 'noise', 'music'], required=True)
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--length', type=float, default=0)
    ap.add_argument('--cut-off', action='store_true')
    ap.add_argument('--work-directory')
    args = ap.parse_args()
    source = Path(args.input).resolve()
    destination = Path(args.destination).resolve()
    engine.ROOT = Path(args.engine).resolve()
    if not source.is_file() or not destination.is_dir():
        raise ValueError('Choose an existing video and destination folder.')
    if args.start < 0 or args.length < 0:
        raise ValueError('Test start and length cannot be negative.')
    if args.mode != 'off':
        (engine.ROOT / 'CACHE').mkdir(exist_ok=True)
    threshold, margin, smooth, tag = ('', '', '', 'NO_CUT') if args.cut_off else resolve(args.profile, engine.PRESETS, args.strength, args.gentle_preset, args.threshold, args.padding, args.pause, args.level)
    for name in (('ffmpeg', 'ffprobe') if args.cut_off else ('ffmpeg', 'ffprobe', 'auto-editor')):
        if not shutil.which(name):
            raise ValueError('Missing ' + name + '. Use Install cleanup tools to run setup.')
    if args.mode == 'noise' and not os.access(engine.ROOT / 'tools/runtime/deep-filter', os.X_OK):
        raise ValueError('Noise tools are missing. Choose your working v4 folder with Use existing v4 setup, or install cleanup tools.')
    if args.mode == 'music' and not all(p.exists() for p in [engine.ROOT / 'tools/music-env/bin/python', engine.ROOT / 'tools/models' / engine.MODEL]):
        raise ValueError('Music tools are missing. Choose your working v4 folder with Use existing v4 setup, or install cleanup tools.')
    info = engine.probe(source)
    original_duration = float(info['format']['duration'])
    start = args.start if args.length else 0
    if start >= original_duration:
        raise ValueError('Test start must be before the end of the video.')
    work_directory = Path(args.work_directory).resolve() if args.work_directory else destination
    work_directory.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix=time.strftime('Silence_Cutter_%Y%m%d_%H%M%S_'), dir=work_directory))
    target = run / (source.stem + '_' + tag + '_' + args.mode.upper() + '_CLEAN.mp4')
    logpath = run / 'PROCESS.log'
    emit('log', path=str(logpath))
    try:
        with logpath.open('w') as log, tempfile.TemporaryDirectory(prefix='temporary_', dir=run) as tempdir:
            temp = Path(tempdir)
            ready = source
            if args.length:
                emit('stage', message='Preparing test excerpt…')
                ready = temp / 'excerpt.mov'
                # Accurate input decoding trims the requested excerpt; full runs avoid this pass.
                engine.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', source,
                            '-ss', str(start), '-t', str(args.length), '-map', '0:v:0', '-map', '0:a:0',
                            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
                            '-c:a', 'pcm_s16le', ready], log)
            if args.mode != 'off':
                emit('stage', message='Preparing local audio cleanup…')
                ready = engine.cleaned_source(ready, args.mode, temp, log,
                            lambda m: emit('stage', message=m))
            input_duration = float(engine.probe(ready)['format']['duration'])
            options = []
            if args.cut_off:
                emit('stage', message='Cutting Off — preserving all pauses…')
                clips = [dict(start=0.0, duration=input_duration, source=start)]
            else:
                emit('stage', message='Finding pauses and building comparison timeline…')
                options = ['auto-editor', ready, '--edit', 'audio:threshold=' + threshold,
                           '--margin', margin, '--smooth', smooth, '--no-open']
                timeline_path = temp / 'timeline.v3'
                engine.run(options + ['--export', 'v3', '-o', timeline_path], log)
                timeline = json.loads(timeline_path.read_text())
                clips = mapping(timeline, start)
            planned_duration = max(c['start'] + c['duration'] for c in clips)
            emit('stage', message='Rendering the video…')
            render(ready, options, target, log, args.cut_off)
            rendered = engine.probe(target)
            kinds = {s['codec_type'] for s in rendered['streams']}
            if not {'audio', 'video'}.issubset(kinds):
                raise ValueError('The rendered output has no usable audio/video pair.')
            duration = float(rendered['format']['duration'])
            if duration <= 0 or abs(duration - planned_duration) > 0.15:
                raise ValueError('Rendered duration does not match the comparison timeline.')
            report = dict(source=str(source), output=str(target), log=str(logpath),
                          inputDuration=input_duration, outputDuration=duration,
                          sourceOffset=start, clips=clips, strength=int(args.strength) if args.profile=='standard' else None, mode=args.mode,
                          profile='off' if args.cut_off else args.profile, level=args.level if args.profile=='scale' and not args.cut_off else None, preset=tag, threshold=threshold, padding=margin, smooth=smooth,
                          removedPercent=0.0 if args.cut_off else max(0, 100 * (1 - duration / input_duration)))
            (run / 'comparison.json').write_text(json.dumps(report, indent=2))
            (run / 'SUMMARY.txt').write_text(
                f'Source: {source}\nOutput: {target}\nProfile: {"off" if args.cut_off else args.profile} / {tag}\nLevel: {args.level if args.profile=="scale" else "custom/legacy"}\nThreshold: {threshold}\nPadding: {margin}\nMinimum cut/clip: {smooth}\nCleanup: {args.mode}\n'
                f'Input/excerpt: {input_duration:.3f}s\nEdited: {duration:.3f}s\n'
                f'Removed: {report["removedPercent"]:.1f}%\nKept segments: {len(clips)}\n'
                f'Test source offset: {start:.3f}s\n')
            emit('done', **report)
    except BaseException:
        target.unlink(missing_ok=True)
        raise


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        emit('cancelled', message='Cancelled. No completed output was saved.')
        sys.exit(130)
    except Exception as exc:
        emit('error', message=str(exc))
        sys.exit(1)
