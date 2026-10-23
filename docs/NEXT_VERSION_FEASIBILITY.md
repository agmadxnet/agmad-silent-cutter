# Proposed additions after the compatibility fix

Status: feasibility assessed; not implemented in the app.

## Keep the existing default workflow

Main controls remain file, destination, cut level and cleanup. Add optional expandable Export options and a separate Clips view. Default watermark Off, playback speed 1.0x and full-video export preserve existing behavior.

## Branding

A local PNG/logo overlay can be positioned on the video preview canvas, with corner presets, safe margins, size and 0–100% opacity. Start with one image overlay; text watermarking can follow after font/Arabic rendering checks. A preview canvas is part of the app and does not require the Canva service. An external Canva integration would be a separate scope. Rendering overlays needs video encoding; avoiding a second full-length encode requires integration into the final render pipeline.

## Speed

Uniform exported playback speed is possible using video timestamp scaling and audio tempo adjustment. Start with 0.75x/1x/1.25x/1.5x/2x, preserve audio pitch, and apply speed after silence decisions. Linked playback and comparison statistics must account for the speed factor. Render-performance settings are a separate option: hardware encoding and faster encoder presets need quality, compatibility and timing benchmarks on actual Mac hardware. Faster output playback does not guarantee faster rendering.

## Selected clips

Manual Mark start / Mark end controls, a named range list, and Export selected clips can produce separate MP4s. Define ranges against the edited timeline and map them to source positions; validate boundaries, overlapping ranges and speed interactions. An explicit Original/Edited timeline label avoids ambiguous timestamps. Start with existing framing. Vertical 9:16 crop/repositioning is a separate useful phase because it can remove people or presentation text and needs its own preview.

## Technical checks completed

Using installed FFmpeg: positioned 25% white overlay on black measured RGB 64/64/64; 1.25x export changed 6 seconds to 4.833 seconds with audio/video present; two selected 1.5-second ranges exported separately. These isolated demonstrations validate engine capability, not finished UI or combined-feature performance.

## Order

1. Validate the 1.4.1 compatibility fix on the reported recording.
2. Branding plus uniform playback speed in optional export controls.
3. Clip range selection and separate exports.
4. Consider vertical crop only after the clip workflow is accepted.

Scope excludes a multitrack editor, effects timeline and automated highlight detection. Keep every added control optional and preserve originals and prior results.
