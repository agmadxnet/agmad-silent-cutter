# Processing and storage

The Mac interface is Swift/AppKit/AVKit. Windows uses readable Python with dynamically linked PySide6/Qt and a bundled CPython runtime. Platform adapters invoke local tools through argument lists. Windows cooperative cancellation stops the active child tree; Mac jobs use their own process group. Settings identifiers and storage directories remain the same as 1.3.

Pipeline: optionally extract a test excerpt → optional local cleanup → Auto-Editor v3 timeline → FFmpeg H.264/AAC render → duration/stream verification → linked comparison report. The timeline maps edited positions to original positions across cuts. Custom/scale resolution lives in identical `cut_settings.py` copies; tests enforce parity. The first audio track is used. Cleanup replaces the soundtrack with cleaned mono speech. Multiple audio-track preservation, HDR/colour-workflow certification, batch processing and speech transcription are outside this release.

Noise uses DeepFilterNet with delay compensation. Music uses audio-separator and UVR-MDX-NET-Inst_HQ_3.onnx. Cleanup caches are keyed by source metadata and settings; changing the cut level can reuse cleaned audio. An existing cache is an optimization, not an archive or tamper-proof media store. Severe wind distortion and speech hidden by other audio may remain unrecoverable.

Source/engine/data ownership:

- `macos/Source/` holds the native app and payload. Bundled payload is copied to managed writable storage; processing does not write inside Applications.
- `windows/app/` holds the GUI, setup, paths and platform adapters. `windows/assets/` holds pinned setup metadata, runtime metadata, icons and style.
- Mac managed storage: `~/Library/Application Support/Agmad Silent Cutter`; an explicitly selected legacy v4 directory remains supported.
- Windows managed storage: `%LOCALAPPDATA%\Agmad Silent Cutter`; installed app: `%LOCALAPPDATA%\Programs\Agmad Silent Cutter`.
- Output: a uniquely named run directory under the selected destination, with MP4, PROCESS.log, SUMMARY.txt and comparison.json.

Originals are opened for reading and are never overwritten. Cancellation removes the job's partial output and temporary media; completed cleanup cache may remain. New version directories do not replace old release artifacts in this source project.
