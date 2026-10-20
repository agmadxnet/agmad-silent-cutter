"""Per-user installation and icon shortcuts. Run with bundled Python."""
import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
from paths import ROOT

def main():
    if os.name!='nt':raise RuntimeError('This installer runs on Windows only.')
    destination=Path(os.environ['LOCALAPPDATA'])/'Programs'/'Agmad Silent Cutter'
    print('جارٍ تثبيت Agmad Silent Cutter للمستخدم الحالي…',flush=True)
    if ROOT.resolve()!=destination.resolve():shutil.copytree(ROOT,destination,dirs_exist_ok=True)
    try:ctypes.WinDLL(str(destination/'runtime/Lib/site-packages/PySide6/msvcp140.dll'))
    except OSError:
        print('يلزم تثبيت Microsoft Visual C++ لتشغيل الواجهة. قد تظهر نافذة موافقة Windows.',flush=True)
        redist=destination/'vc_redist.x64.exe'
        urllib.request.urlretrieve('https://aka.ms/vs/17/release/vc_redist.x64.exe',redist)
        result=subprocess.run([str(redist),'/install','/passive','/norestart'])
        if result.returncode not in (0,1638,3010):raise RuntimeError('لم يكتمل تثبيت Microsoft Visual C++. أعد المحاولة.')
        redist.unlink(missing_ok=True)
    env=os.environ.copy();env['AGMAD_TARGET']=str(destination/'runtime/pythonw.exe');env['AGMAD_ARGS']='"'+str(destination/'app/launcher.py')+'"'
    env['AGMAD_WORK']=str(destination);env['AGMAD_ICON']=str(destination/'assets/icon.ico')
    ps="""$w=New-Object -ComObject WScript.Shell; foreach($folder in @([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('Programs'))){$s=$w.CreateShortcut((Join-Path $folder 'Agmad Silent Cutter.lnk'));$s.TargetPath=$env:AGMAD_TARGET;$s.Arguments=$env:AGMAD_ARGS;$s.WorkingDirectory=$env:AGMAD_WORK;$s.IconLocation=$env:AGMAD_ICON;$s.Save()}"""
    subprocess.run(['powershell.exe','-NoProfile','-Command',ps],env=env,check=True)
    print('اكتمل التثبيت. افتح أيقونة Agmad Silent Cutter من سطح المكتب.',flush=True)
if __name__=='__main__':
    try:main()
    except Exception as exc:print('تعذر التثبيت: '+str(exc),flush=True);sys.exit(1)
