# Mac 1.5.0 watermark test build

Status: local Mac test package. No public release, Windows build or site update.

## Use

1. Choose a video and destination as usual. Watermark is Off by default.
2. Choose PNG. The checkbox turns on; the file stays on your computer.
3. Open Position & opacity. Click/drag on the first-frame preview or choose a corner/Centre preset.
4. Set Size (5–40% of video width) and Opacity (0–100%). Tall logos are capped to 80% of video height. PNG transparency is multiplied by the opacity setting.
5. Click Use watermark. Cancel discards placement edits.
6. Process a 30-second test and review the actual result. The watermark appears throughout the export; editing settings afterward applies to the next run.

The logo is one static PNG, max 20 MB and 8192 pixels per dimension. Watermark selection/settings are session-only; no automatic branding on a later app launch. The placement preview is a still frame, not a live overlay on the player. FFmpeg provides a fallback preview for codecs the native image generator cannot decode.

## Processing

Watermark Off uses the existing adapter unchanged. Enabled branding wraps that adapter and adds a final H.264 video encoding pass (CRF 18, fast preset); AAC audio is copied. This costs additional render time and a temporary unbranded MP4, and adds a lossy video generation. Use Off when branding is not needed. Opacity zero skips the finishing pass. The wrapper cleans its temporary directory on unwinding; the existing adapter handles partial final-output cleanup. Cutting settings, timeline, cleanup modes and storage identifiers remain unchanged. Watermark metadata is written into comparison.json and SUMMARY.txt.

The AV1 cleanup compatibility fix from 1.4.1 is retained. Playback-speed controls and separate Shorts export are not included.

## Validation

Real exports check 0/25/100% opacity and a transparent PNG combined with 50% opacity, expected pixel position/brightness, unchanged comparison duration, invalid-value rejection and temporary-directory cleanup after success. Existing cutting/cleanup regression tests remain enabled. Native UI smoke checks exercise the sheet, sliders and placement bounds; full native app export checks load both linked players. See the owner workspace work/watermark150 for test captures and exact results. No long branded production recording or native Windows watermark test is claimed.
