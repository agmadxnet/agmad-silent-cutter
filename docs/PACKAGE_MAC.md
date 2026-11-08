# AGMAD Silent Cutter — Mac installation and use

## Install or update

Apple Silicon and macOS 14+ are required. Quit the old app, open the DMG and drag **Agmad Silent Cutter.app** into Applications. Replace the previous app if prompted, then eject the DMG. The ZIP is an alternative. Existing settings, installed tools, models and results are retained.

The app is ad-hoc signed, not Apple Developer ID signed or notarized. Review the download and use the approval for this specific app in System Settings → Privacy & Security if needed; do not disable system security globally.

Initial processing-tool setup needs Homebrew and internet. Reuse working tools when updating. Media processing runs locally; optional Music setup downloads additional dependencies/models.

## Use

1. Choose a video and destination.
2. Select the −5…+5 scale, bounded Custom settings, or Cutting Off. Level 0 still removes pauses; Off keeps them.
3. Select audio cleanup Off, Noise or Music independently of cutting.
4. Optionally choose a PNG watermark and adjust position, size and opacity.
5. Select the output filename style and optional prefix.
6. Test 30 seconds, review the linked players, speech and lip sync, then export the full recording.

Completed MP4s go directly into the selected destination. Originals and existing outputs are protected against overwriting. Processing reports, cache and logs remain in managed application storage, normally under `~/Library/Application Support/Agmad Silent Cutter`.

Cutting Off still encodes H.264/AAC. Watermarks add an encoding pass. Noise/Music cleanup can introduce artifacts; Music uses more resources. No batch queue, exported playback-speed control or vertical crop is included.

## Evidence and licenses

Read the accompanying VALIDATION.md for dated test evidence and its limits; historical results do not certify a newly built package. Review outputs on your own device. Application source and original artwork are MIT; third-party tools/models retain their licenses. Keep LICENSE and THIRD_PARTY_NOTICES.md with the package.
