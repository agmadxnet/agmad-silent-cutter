import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get('AGMAD_TEST_DATA') or (Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'Agmad Silent Cutter'))
BIN = DATA / 'tools' / 'runtime'
def prepare():
    for name in ('tools', 'LOGS', 'CACHE', 'tools/runtime', 'tools/models'):
        (DATA / name).mkdir(parents=True, exist_ok=True)
    source = ROOT / 'app/tools/music.py'
    (DATA / 'tools/music.py').write_bytes(source.read_bytes())
    os.environ['PATH'] = str(BIN) + os.pathsep + os.environ.get('PATH', '')
    os.environ['AGMAD_MUSIC_PYTHON'] = str(ROOT / 'runtime/python.exe') if os.name=='nt' else os.environ.get('AGMAD_MUSIC_PYTHON', os.sys.executable)
