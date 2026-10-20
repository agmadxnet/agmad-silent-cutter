#!/bin/bash
set -e
cd "$(dirname "$0")" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
mkdir -p LOGS tools/runtime tools/models
# Preserve diagnostics in Terminal and in the package.
exec > >(tee LOGS/SETUP.log) 2>&1
trap 'echo "Setup failed. Read LOGS/SETUP.log. Off still works if Auto-Editor is installed."' ERR
command -v brew >/dev/null || { echo 'Install Homebrew first: https://brew.sh'; exit 1; }
for formula in ffmpeg auto-editor python@3.12; do
  if ! brew list --versions "$formula" >/dev/null 2>&1; then brew install "$formula"; fi
done
case "$(uname -m)" in arm64) arch=aarch64; expected=4601e7f4e4c03e59a4c5b5000216ef3add3e808799cfccd95e14e83ea4611081 ;; *) echo 'This full cleanup setup requires an Apple Silicon Mac. Off can still be used on Intel.'; exit 1 ;; esac
if [ ! -x tools/runtime/deep-filter ]; then
  curl -fL --retry 2 "https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/deep-filter-0.5.6-${arch}-apple-darwin" -o tools/runtime/deep-filter.download
  actual=$(shasum -a 256 tools/runtime/deep-filter.download | awk '{print $1}')
  [ "$actual" = "$expected" ] || { echo 'Noise engine checksum mismatch.'; exit 1; }
  chmod +x tools/runtime/deep-filter.download
  mv tools/runtime/deep-filter.download tools/runtime/deep-filter
fi
tools/runtime/deep-filter --version
PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
if [ ! -x tools/music-env/bin/python ]; then "$PYTHON" -m venv tools/music-env; fi
tools/music-env/bin/python -m pip install -r tools/requirements-music.txt
tools/music-env/bin/python tools/music.py download
tools/music-env/bin/python -m pip freeze > tools/installed-versions.txt
shasum -a 256 tools/runtime/deep-filter tools/models/UVR-MDX-NET-Inst_HQ_3.onnx > tools/engine-checksums.txt
echo 'Setup complete. Daily use: Run_Silence_Cutter.command. Select strength, then Noise/Music/Off.'
