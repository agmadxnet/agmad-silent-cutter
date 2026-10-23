# AGMAD Silent Cutter 1.5.1

Local video silence cutting, optional voice cleanup and PNG watermarking for Mac and Windows.

**Release prepared for approval; public release remains 1.4.0 until publication.** The owner reports the delivered Mac and Windows 1.5.1 tests passed. See [release notes](docs/RELEASE_1.5.1.md) and [validation](docs/WINDOWS_1.5.1_VALIDATION.md) for evidence and limits.

## Workflow

1. Choose a video and output folder.
2. Choose −5…+5, bounded Custom values, or Cutting Off to keep all pauses. Audio cleanup Off/Noise/Music is independent.
3. Optionally place a PNG watermark, adjust size and opacity.
4. Choose original name, date, date + name or numeric serial, with an optional prefix.
5. Test 30 seconds, compare the linked players and lip sync, then export the full video.

Originals remain intact. New MP4s go directly into the chosen folder; processing reports remain internal. Existing names are never overwritten. Watermarking adds an encoding pass; Cutting Off still encodes H.264/AAC. No batch queue, export-speed control, Shorts selection, vertical crop, cloud processing or account is included.

## Install

Mac: Apple Silicon/macOS 14+, initial Homebrew tools setup. Quit the old app and drag the app from the DMG into Applications. [Mac update guide](docs/MAC_EXPORT_TEST.md).

Windows: Intel/AMD 64-bit; extract the complete ZIP, run Install.cmd. Python/Qt is bundled. [الدليل العربي](docs/WINDOWS_1.5.1_TEST.ar.md).

Settings/tools/models/results are retained. Accepted installers retain their build-time test labels; release filenames do not imply a rebuild. Noise/Music can introduce artifacts; optional Music setup is heavier.

## Development and license

Run `python3 -m unittest discover -s tests -v`. See [build guide](docs/BUILD.md), [architecture](docs/ARCHITECTURE.md), [privacy](docs/PRIVACY.md) and [third-party notices](THIRD_PARTY_NOTICES.md). No fresh hosted CI pass is claimed.

Application source and original waveform artwork: [MIT](LICENSE). Third-party tools/models keep their licenses. Mac is ad-hoc signed, not Apple-notarized; Windows is not publisher-signed. No model weights, private recordings or installed environments are included in source.
