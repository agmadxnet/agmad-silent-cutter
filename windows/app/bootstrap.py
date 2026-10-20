"""Explicit, local, per-user engine setup. No system PATH or admin changes."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from paths import ROOT, DATA, BIN, prepare

def emit(event,**values):print(json.dumps(dict(event=event,**values)),flush=True)
def check_cancel():
    path=os.environ.get('AGMAD_CANCEL_FILE')
    if path and Path(path).exists():raise KeyboardInterrupt()
def download(spec,target):
    emit('stage',message='تنزيل '+spec['name']+'…')
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==spec['sha256']:return
    part=target.with_suffix(target.suffix+'.download');h=hashlib.sha256()
    try:
        with urllib.request.urlopen(spec['url'],timeout=90) as response,part.open('wb') as out:
            while True:
                check_cancel();chunk=response.read(1024*1024)
                if not chunk:break
                out.write(chunk);h.update(chunk)
        if h.hexdigest()!=spec['sha256']:raise ValueError('فشل التحقق من سلامة التنزيل: '+spec['name'])
        os.replace(part,target)
    finally:part.unlink(missing_ok=True)
def command(args,log):
    flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
    child=subprocess.Popen([str(a) for a in args],stdout=log,stderr=log,creationflags=flags)
    try:
        while child.poll() is None:check_cancel();time.sleep(.2)
        if child.returncode:raise RuntimeError('فشل تثبيت المكتبات. راجع سجل التثبيت.')
    except BaseException:
        if child.poll() is None:
            if os.name=='nt':subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],stdout=log,stderr=log,creationflags=flags)
            else:child.terminate()
            child.wait(timeout=20)
        raise

def main():
    prepare();which=sys.argv[1]
    manifest=json.loads((ROOT/'assets/downloads.json').read_text())
    path=DATA/'LOGS'/('setup_'+time.strftime('%Y%m%d_%H%M%S')+'.log');emit('log',path=str(path))
    with path.open('w',encoding='utf-8') as log:
        try:
            if which=='core':
                download(manifest['auto-editor'],BIN/'auto-editor.exe')
                download(manifest['deep-filter'],BIN/'deep-filter.exe')
                with tempfile.TemporaryDirectory(dir=DATA) as temp:
                    archive=Path(temp)/'ffmpeg.zip';download(manifest['ffmpeg'],archive)
                    with zipfile.ZipFile(archive) as z:
                        for executable in ('ffmpeg.exe','ffprobe.exe'):
                            name=next(n for n in z.namelist() if n.endswith('/bin/'+executable))
                            staging=BIN/(executable+'.new');staging.write_bytes(z.read(name));os.replace(staging,BIN/executable)
                for executable,flag in [('auto-editor.exe','--version'),('deep-filter.exe','--version'),('ffmpeg.exe','-version')]:command([BIN/executable,flag],log)
                emit('ready',message='اكتمل تثبيت أدوات المعالجة. يمكنك الآن استخدام بدون تنظيف أو إزالة الضوضاء.')
            elif which=='music':
                if not (BIN/'ffmpeg.exe').exists():raise ValueError('ثبّت أدوات المعالجة الأساسية أولًا.')
                emit('stage',message='تثبيت مكتبات فصل الموسيقى على المعالج — قد يستغرق عدة دقائق…')
                staging=Path(tempfile.mkdtemp(prefix='music_packages_',dir=DATA/'tools'))
                try:
                    command([sys.executable,'-m','pip','install','--no-warn-script-location','--only-binary=:all:',
                        '--target',staging,'--extra-index-url','https://download.pytorch.org/whl/cpu',
                        '--require-hashes','-r',ROOT/'assets/music-requirements.txt'],log)
                    live=DATA/'tools/music-packages';previous=DATA/'tools/music-packages.previous'
                    if previous.exists():shutil.rmtree(previous)
                    if live.exists():live.rename(previous)
                    staging.rename(live)
                    emit('stage',message='تنزيل نموذج الصوت وتجهيزه للعمل محليًا…')
                    command([sys.executable,DATA/'tools/music.py','download'],log)
                    if previous.exists():shutil.rmtree(previous)
                    emit('ready',message='اكتمل تثبيت تنظيف الموسيقى. المعالجة التالية محلية.')
                finally:
                    if staging.exists():shutil.rmtree(staging)
            else:raise ValueError('Unknown setup selection')
        except BaseException as exc:
            log.write(repr(exc)+'\n');raise
if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:emit('cancelled',message='تم إلغاء التثبيت. يمكنك إعادة المحاولة.');sys.exit(130)
    except Exception as exc:emit('error',message=str(exc));sys.exit(1)
