import os
from pathlib import Path
import runpy
import traceback
try:
    if os.name=='nt':
        qt=Path(__file__).resolve().parent.parent/'runtime/Lib/site-packages/PySide6'
        os.environ['QT_PLUGIN_PATH']=str(qt/'plugins')
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH']=str(qt/'plugins/platforms')
        dll_directory=os.add_dll_directory(str(qt))
    runpy.run_path(str(Path(__file__).with_name('main.py')), run_name='__main__')
except SystemExit:
    raise
except Exception:
    from paths import DATA
    folder=DATA/'LOGS';folder.mkdir(parents=True,exist_ok=True)
    path=folder/'launch.log';path.write_text(traceback.format_exc(),encoding='utf-8')
    if os.name=='nt':
        import ctypes
        ctypes.windll.user32.MessageBoxW(None,'تعذر فتح البرنامج. شغّل Install.cmd أولًا. سجل الخطأ:\n'+str(path),'Agmad Silent Cutter',0x10)
    else:raise
