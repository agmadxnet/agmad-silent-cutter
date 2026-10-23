#!/usr/bin/env python3
"""Optional branding wrapper; the established cutting adapter stays unchanged."""
import argparse
import json
import math
from pathlib import Path
import sys
import tempfile
import gui_process as adapter


def geometry(width, height, logo_width, logo_height, fraction, x, y):
    size = min(width * fraction, height * .8 * logo_width / logo_height)
    h = max(1, round(size * logo_height / logo_width))
    w = max(1, round(h * logo_width / logo_height))
    return w, h, round((width - w) * x), round((height - h) * y)


def validate(path, width, x, y, opacity):
    for name, value, low, high in [('size', width, .05, .4), ('x', x, 0, 1),
                                   ('y', y, 0, 1), ('opacity', opacity, 0, 1)]:
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError('Watermark ' + name + ' is outside its allowed range.')
    path = Path(path).resolve()
    if not path.is_file() or path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError('Choose a PNG logo smaller than 20 MB.')
    with path.open('rb') as source:
        if source.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError('The watermark must be a PNG image.')
    info = adapter.engine.probe(path)
    image = next((s for s in info['streams'] if s['codec_type'] == 'video'), {})
    w, h = int(image.get('width', 0)), int(image.get('height', 0))
    if not 0 < w <= 8192 or not 0 < h <= 8192:
        raise ValueError('PNG dimensions must be between 1 and 8192 pixels.')
    return path, w, h


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--watermark-file', required=True)
    parser.add_argument('--watermark-width', type=float, default=.15)
    parser.add_argument('--watermark-x', type=float, default=.95)
    parser.add_argument('--watermark-y', type=float, default=.95)
    parser.add_argument('--watermark-opacity', type=float, default=.7)
    wm, rest = parser.parse_known_args()
    logo, lw, lh = validate(wm.watermark_file, wm.watermark_width, wm.watermark_x, wm.watermark_y, wm.watermark_opacity)
    config = dict(file=str(logo), width=wm.watermark_width, x=wm.watermark_x,
                  y=wm.watermark_y, opacity=wm.watermark_opacity)
    render = adapter.render
    emit = adapter.emit

    def branded_render(ready, options, target, log, cut_off=False):
        if wm.watermark_opacity == 0:
            return render(ready, options, target, log, cut_off)
        target = Path(target)
        # Keep the ordinary cutting output private and discard it even on cancellation.
        with tempfile.TemporaryDirectory(prefix='branding_', dir=target.parent) as folder:
            raw = Path(folder) / 'unbranded.mp4'
            render(ready, options, raw, log, cut_off)
            video = next(s for s in adapter.engine.probe(raw)['streams'] if s['codec_type'] == 'video')
            w, h, x, y = geometry(int(video['width']), int(video['height']), lw, lh,
                                   wm.watermark_width, wm.watermark_x, wm.watermark_y)
            emit('stage', message='Applying watermark — additional video encoding pass…')
            graph = (f'[1:v]scale={w}:{h},format=rgba,colorchannelmixer=aa={wm.watermark_opacity}[logo];'
                     f'[0:v][logo]overlay={x}:{y}:shortest=1:format=auto,format=yuv420p[v]')
            adapter.engine.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', raw, '-loop', '1', '-i', logo,
                 '-filter_complex', graph, '-map', '[v]', '-map', '0:a:0', '-c:v', 'libx264',
                 '-preset', 'fast', '-crf', '18', '-c:a', 'copy', '-movflags', '+faststart', target], log)

    def branded_emit(event, **fields):
        if event == 'done':
            fields['watermark'] = config
            output_dir = Path(fields['output']).parent
            report_path = output_dir / 'comparison.json'
            report = json.loads(report_path.read_text(encoding='utf-8'))
            report['watermark'] = config
            report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
            with (output_dir / 'SUMMARY.txt').open('a', encoding='utf-8') as summary:
                summary.write('\nWatermark: ' + json.dumps(config) + '\n')
        emit(event, **fields)

    adapter.render = branded_render
    adapter.emit = branded_emit
    sys.argv = [sys.argv[0]] + rest
    adapter.main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        adapter.emit('cancelled', message='Cancelled. No completed output was saved.')
        sys.exit(130)
    except Exception as exc:
        adapter.emit('error', message=str(exc))
        sys.exit(1)
