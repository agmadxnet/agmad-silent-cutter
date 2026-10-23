# Mac 1.5.1 test build — Cutting Off and video-only exports

Owner reported this Mac 1.5.1 test working on 22 October 2026. Detailed per-option results were not supplied. This remains a local test build, not a public release or Windows update. Retains the 1.4.1 AV1 compatibility fix and 1.5.0 PNG watermark controls. The owner reported the watermark test working before this update.

## Cutting Off

Cutting mode now offers Preset scale, Custom and Off. Off preserves all pauses and hides the cut-strength fields. Noise/Music cleanup and watermarking remain independent and available. A selected 30/60-second test still exports only that excerpt. Off does not invoke or require Auto-Editor, although FFmpeg/FFprobe and any selected cleanup tools remain required. The final video is still encoded as H.264/AAC MP4 for compatibility; Off is not a lossless passthrough mode.

## One export folder

Every new completed video is saved directly into the selected output destination. The app does not create per-video folders or write JSON/log/text sidecars there. Existing exports and originals are not moved or deleted.

Processing reports, comparison data and temporary media are kept in the app's internal Application Support RUNS area. Open report still works, and linked playback still receives its comparison mapping. A completed internal staging MP4 is copied exclusively into the chosen destination, then removed from internal staging. Copy failure/cancellation removes the new partial destination file; earlier exports remain untouched. Temporary copying may briefly show a growing MP4 until saving finishes.

## Filenames

- Original name: `lecture.mp4`
- Date: `2026-10-22.mp4` (local export date)
- Date + name: `2026-10-22_lecture.mp4`
- Numeric serial: `0001.mp4`, `0002.mp4`, …

An optional prefix applies to each style: `AG_lecture.mp4`, `AG_2026-10-22_lecture.mp4`, or `AG_0001.mp4`. The app remembers the selected style/prefix. Prefixes allow up to 60 characters and cannot include slashes/control characters. Long names are shortened safely for the filesystem.

Existing filenames are never overwritten. Name/date collisions add `_002`, `_003`, …; serial naming continues from the largest matching number in the folder. Exclusive creation also protects overlapping exports. When exporting beside the source file with Original name, a suffix protects the original.

## Validation

Seventeen automated checks cover existing cut/cleanup/watermark behavior, Unicode/naming options, overlapping serial exports, source-file protection, copy-failure and cancellation cleanup, flat destination contents, internal report paths, true no-cut renders without Auto-Editor on PATH, cleanup plus Off, watermark plus Off, and normal silence cutting. Native app checks cover Off controls and exports/linked playback. Package-specific results and hashes are in the owner workspace work/export151/VALIDATION.json. No native Windows update is included.

Install: quit Silent Cutter, open the DMG and drag the app to Applications. Existing settings/tools/results are retained. Start with a 30-second test. Apple Silicon/macOS 14+, ad-hoc signed and not Apple-notarized.
