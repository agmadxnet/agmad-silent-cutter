#!/usr/bin/env python3
"""Publish only videos to the selected folder; keep job reports internally."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import shutil
import sys
import gui_process as adapter


def validate_prefix(value):
    value = value.strip()
    if len(value) > 60 or any(c in '/\\' or ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError('Filename prefix: use up to 60 characters without slashes or control characters.')
    if value in {'.', '..'}:
        raise ValueError('Choose a filename prefix other than dots.')
    return value


def filename_base(source, style, prefix='', today=None):
    prefix = validate_prefix(prefix)
    stem = re.sub(r'[\\/\x00-\x1f\x7f]', '_', Path(source).stem).strip(' .') or 'video'
    stamp = (today or date.today()).isoformat()
    name = {'name':stem, 'date':stamp, 'date-name':stamp+'_'+stem}.get(style)
    if name is None:
        raise ValueError('Choose a valid filename style.')
    value = (prefix+'_' if prefix else '')+name
    return value.encode('utf-8')[:220].decode('utf-8',errors='ignore')


def publish(video, destination, source, style, prefix=''):
    """Exclusive file creation works on external filesystems without hard links."""
    video, destination = Path(video), Path(destination)
    prefix = validate_prefix(prefix)
    if style == 'serial':
        lead = prefix+'_' if prefix else ''
        pattern = re.compile(re.escape(lead)+r'(\d+)\.mp4$',re.I)
        used = [int(m.group(1)) for p in destination.iterdir() if (m:=pattern.fullmatch(p.name))]
        number = max(used,default=0)+1
        base = None
    else:
        base = filename_base(source,style,prefix)
        number = 1
    while True:
        name = f'{lead}{number:04d}.mp4' if base is None else base+(f'_{number:03d}' if number>1 else '')+'.mp4'
        target = destination/name
        try:
            handle = target.open('xb')
            break
        except FileExistsError:
            number += 1
    try:
        with handle, video.open('rb') as src:
            shutil.copyfileobj(src,handle,length=1024*1024)
            handle.flush();os.fsync(handle.fileno())
        if target.stat().st_size != video.stat().st_size:
            raise ValueError('Video copy was incomplete; check free disk space.')
        return target
    except BaseException:
        target.unlink(missing_ok=True)
        raise


def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--filename-style',choices=['name','date','date-name','serial'],default='name')
    parser.add_argument('--filename-prefix',default='')
    parser.add_argument('--reports-root',required=True)
    args, rest=parser.parse_known_args()
    args.filename_prefix=validate_prefix(args.filename_prefix)
    # Parse shared paths without taking ownership of the cutting/cleanup options.
    shared=argparse.ArgumentParser(add_help=False)
    shared.add_argument('--input',required=True);shared.add_argument('--destination',required=True)
    paths,_=shared.parse_known_args(rest)
    source=Path(paths.input).resolve();destination=Path(paths.destination).resolve()
    reports=Path(args.reports_root).resolve()
    if not source.is_file() or not destination.is_dir():
        raise ValueError('Choose an existing video and destination folder.')
    if reports == destination or destination in reports.parents:
        raise ValueError('Internal reports must be stored outside the video export folder.')
    reports.mkdir(parents=True,exist_ok=True)
    emit=adapter.emit

    def export_emit(event,**fields):
        if event=='done':
            temporary=Path(fields['output'])
            emit('stage',message='Saving video to the export folder…')
            exported=publish(temporary,destination,source,args.filename_style,args.filename_prefix)
            fields['output']=str(exported)
            fields['filenameStyle']=args.filename_style
            fields['filenamePrefix']=args.filename_prefix
            report_path=temporary.parent/'comparison.json'
            report=json.loads(report_path.read_text());report.update(output=str(exported),filenameStyle=args.filename_style,filenamePrefix=args.filename_prefix)
            report_path.write_text(json.dumps(report,indent=2))
            summary=temporary.parent/'SUMMARY.txt'
            summary.write_text(summary.read_text().replace('Output: '+str(temporary),'Output: '+str(exported)))
            temporary.unlink()
        emit(event,**fields)

    adapter.emit=export_emit
    sys.argv=[sys.argv[0]]+rest+['--work-directory',str(reports)]
    if '--watermark-file' in rest:
        import watermark_process
        watermark_process.main()
    else:
        adapter.main()

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:
        adapter.emit('cancelled',message='Cancelled. No completed output was saved.');sys.exit(130)
    except Exception as exc:
        adapter.emit('error',message=str(exc));sys.exit(1)
