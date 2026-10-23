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

Mac watermark test build: optional watermark_process.py wraps the unchanged GUI adapter only when branding is enabled. It validates a static PNG and normalized placement, then applies a finishing FFmpeg overlay pass. Mac Watermark.swift supplies a still-frame drag/size/opacity sheet. Original/edited timing remains unchanged; normal cutting uses its existing path. See WATERMARK_MAC_TEST.md for the extra encoding/disk tradeoff.

Mac 1.5.1 test build adds export_process.py: it invokes the cutting/watermark pipeline with job storage under Application Support/RUNS, then publishes only the verified MP4 directly to the selected destination using exclusive file creation. Reports and linked comparison data remain internal. gui_process.render is the explicit extension point for watermarking and supports a no-cut FFmpeg path. Filename styles and optional prefix live in the native Mac UI. See MAC_EXPORT_TEST.md. The historical 1.3 baseline remains stored, alongside an explicit 1.5.1 baseline for the deliberately updated Mac adapters.

## Windows 1.5.1 test port

The Arabic Qt interface now invokes tools/export_process.py, keeping RUNS under per-user application data and publishing only MP4 files into the selected destination. The Mac adapter behavior is ported with Windows-specific cooperative cancellation, child-tree termination, deep-filter.exe/music paths, UTF-8 reports and reserved-filename handling preserved. The watermark render calls the current engine.run after the Windows cancellation hook is installed, including the extra overlay encode. Copy publication checks the cancellation file between chunks and removes only its partial destination on failure/cancellation.

windows/app/watermark.py provides a session-only PNG dialog, local FFmpeg still-frame preview, aspect-preserving drag/corner placement, size and opacity. No external service or dependency is added. The scrollable main view supports small displays. Existing scale/custom values and per-user storage remain; Cutting Off is a separate third mode. The Windows adapter extension has its own explicit baseline manifest; the Mac baseline remains unchanged. See WINDOWS_1.5.1_TEST.ar.md and WINDOWS_1.5.1_VALIDATION.md for testing limits.
