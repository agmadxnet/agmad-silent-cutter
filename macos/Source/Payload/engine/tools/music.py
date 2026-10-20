"""Pinned local UVR model: download during setup; separate to a voice-only WAV."""
from pathlib import Path
import sys
from audio_separator.separator import Separator
if sys.argv[1] == 'separate':
    # Dependencies and model metadata are downloaded during setup only.
    import requests
    def no_network(*args, **kwargs):
        raise RuntimeError('Offline mode: a model/setup file is missing. Run Setup_Local_Audio.command.')
    requests.sessions.Session.request = no_network
root = Path(__file__).resolve().parent
separator = Separator(model_file_dir=str(root / 'models'),
                      output_dir=str(Path(sys.argv[3])) if sys.argv[1] == 'separate' else str(root / 'models'),
                      output_format='WAV', output_single_stem='Vocals',
                      normalization_threshold=1.0, amplification_threshold=0.0)
separator.load_model(model_filename='UVR-MDX-NET-Inst_HQ_3.onnx')
if sys.argv[1] == 'separate':
    separator.separate(sys.argv[2])
