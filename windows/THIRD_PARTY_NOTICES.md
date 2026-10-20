# Third-party components

The Windows distribution includes unmodified official CPython 3.13.16 Windows embeddable runtime, pip 26.2.1, PySide6 6.8.3 and Shiboken6 6.8.3 Windows wheels. LGPLv3/GPLv3 texts are included in LICENSES/. Original wheel notices are retained in runtime/LICENSE.txt and the corresponding runtime/Lib/site-packages/*dist-info license directories, including the upstream Qt commercial-option notice. The LGPL option is used for the retained dynamically linked Qt widgets/multimedia components. Qt is dynamically linked; components may be replaced under their applicable licenses. This package imposes no restriction on reverse engineering for debugging modifications to LGPL components.

Project/source locations:
- Python: https://www.python.org/downloads/release/python-31316/ and https://github.com/python/cpython/tree/v3.13.16
- Pip: https://github.com/pypa/pip/tree/26.2.1 (MIT)
- PySide6 / Shiboken6 6.8.3 source: https://download.qt.io/official_releases/QtForPython/pyside6/ . Bindings are available under LGPLv3/GPLv3/commercial terms as stated in included notices.
- Qt 6.8.3 corresponding source: https://download.qt.io/archive/qt/6.8/6.8.3/single/ . Applicable Qt module licenses are included in the distributed wheel notices.

Downloaded by explicit setup, not redistributed in this package:
- Auto-Editor 31.7.2: https://github.com/WyattBlue/auto-editor/releases/tag/31.7.2
- DeepFilterNet 0.5.6: https://github.com/Rikorose/DeepFilterNet/releases/tag/v0.5.6 (MIT/Apache-2.0 project)
- FFmpeg 9.0.2 essentials GPL build by Gyan: https://github.com/GyanD/codexffmpeg/releases/tag/9.0.2 . Build information/source links: https://www.gyan.dev/ffmpeg/builds/ and https://github.com/FFmpeg/FFmpeg . This build includes libx264 and is GPL, not LGPL-only.
- Optional audio-separator 0.47.0 and dependencies: https://github.com/nomadkaraoke/python-audio-separator . UVR/MDX model work: https://github.com/Anjok07/ultimatevocalremovergui and associated contributors. Each downloaded library/model retains its own license.
- Microsoft Visual C++ runtime, if required: official Microsoft redistributable at https://aka.ms/vs/17/release/vc_redist.x64.exe, subject to Microsoft's terms.

The original silver waveform icon and its build script are part of the AGMAD source. See branding/README.md and assets/ICON.md.

The app source is delivered as readable Python files under app/. The retained bundled third-party binary libraries are unmodified; unused browser/3D modules have been omitted (see assets/runtime-components.json); no model weights, sample recordings, or processing-engine executables are redistributed here. Official engine downloads are pinned by version and SHA-256 in assets/downloads.json. Optional Windows CPU music dependencies are pinned by version and hash in assets/music-requirements.txt.
