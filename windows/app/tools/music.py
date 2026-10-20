from pathlib import Path
import sys
import os
os.environ.setdefault("OMP_NUM_THREADS","2")
os.environ.setdefault("MKL_NUM_THREADS","2")
root = Path(__file__).resolve().parent
packages = root / 'music-packages'
if packages.exists(): sys.path.insert(0, str(packages))
from audio_separator.separator import Separator
if sys.argv[1] == 'separate':
    import requests
    def offline(*args, **kwargs): raise RuntimeError('Missing offline model file. Run Music setup again.')
    requests.sessions.Session.request = offline
separator = Separator(model_file_dir=str(root / 'models'),
    output_dir=str(Path(sys.argv[3])) if sys.argv[1]=='separate' else str(root / 'models'),
    output_format='WAV', output_single_stem='Vocals', normalization_threshold=1.0, amplification_threshold=0.0)
separator.load_model(model_filename='UVR-MDX-NET-Inst_HQ_3.onnx')
if sys.argv[1]=='separate': separator.separate(sys.argv[2])
