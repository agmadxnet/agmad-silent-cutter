# AGMAD Silent Cutter 1.5.1 — release notes

Status: [published stable release](https://github.com/agmadxnet/agmad-silent-cutter/releases/tag/v1.5.1), verified 2026-11-08. The release lists 12 attachments, including Mac DMG/ZIP, Windows ZIP, source and SHA256SUMS. Historical preparation records inside the unchanged assets may retain pre-release wording.

## What changes

- Add a PNG logo or watermark, drag it on a local still-frame preview, choose a corner/centre, adjust size and 0–100% opacity. PNG transparency is preserved. Watermarking starts Off in each session.
- Cutting mode now includes Off, independently of audio cleanup and watermarking. Off keeps pauses; scale −5…+5 and bounded Custom settings remain available.
- Save every new completed MP4 directly into one selected destination. Processing logs and comparison reports stay in internal application storage.
- Choose original name, local date, date + name or numeric serial, with an optional prefix. Existing files and source recordings are protected against overwriting.
- Fix cleanup preparation for AV1 recordings by using a compatible temporary Matroska/FLAC container. The original reported 87-minute Mac recording was subsequently reported successful by the owner.
- Keep the native English Mac interface and Arabic Windows interface/instructions. No extra runtime dependency is added.

## Install and review

Quit the old app. Mac: open the DMG and replace the app in Applications. Windows: extract the entire ZIP and run Install.cmd. Existing settings, tools, models and results are retained. Try a short excerpt and check speech, watermark placement, lip sync and destination contents before processing a long video.

Mac requires Apple Silicon/macOS 14+ and initial tool setup through Homebrew. Windows is Intel/AMD 64-bit, with the existing bundled Python/Qt runtime. Optional Music cleanup remains heavier than ordinary cutting. No account or media upload is required by the desktop processing pipeline; explicit setup downloads tools/models.

## Evidence and limits

The owner reported both delivered 1.5.1 platform tests passed. Device details and a per-option Windows/long-recording test breakdown were not supplied. The 18 regression tests passed, alongside Windows-adapter media/pixel checks and Mac-hosted Qt export/linked-playback/cancellation checks. Mac package signatures were verified from extracted ZIP and mounted DMG; the Windows runtime's 1,077 locked files and ZIP/source parity were checked. New hosted CI results are not claimed.

The Mac app is ad-hoc signed, not Apple-notarized. Windows has no publisher signature. The original tested packages retain build-time test labels and documentation; publication copies may use versioned release filenames, but their bytes must match the accepted packages. Rebuilding or editing their contents would require new validation and acceptance.

Cutting Off still encodes to H.264/AAC; it is not lossless passthrough. Watermarking adds a video encoding pass and temporary disk use. Noise/music separation can leave artifacts and may not repair severe wind distortion. Single-file GUI processing remains; no batch queue, exported playback-speed control, automatic highlights, Shorts range selection or vertical reframing is included.

## Downloads and verification

Use the [release page](https://github.com/agmadxnet/agmad-silent-cutter/releases/tag/v1.5.1) for versioned downloads and SHA256SUMS. Verify downloaded bytes against those published checksums. The 2026-11-08 documentation audit checked release metadata and live English/Arabic product-page links; it did not repeat the original binary checksum or runtime tests. Version 1.4.0 remains available. See [status](../STATUS.md) for the historical publication record.
