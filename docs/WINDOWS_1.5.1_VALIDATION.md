# Windows 1.5.1 local test candidate

This candidate ports the accepted Mac 1.5.1 controls to the existing Arabic Qt Windows interface. It includes the AV1 cleanup-container correction, session-only PNG watermark placement/opacity, Cutting Off, flat MP4-only exports and four filename styles with an optional prefix. Public release remains 1.4.0; no live download or release tag was changed.

## Checks performed on macOS

- Existing 17 regression checks plus Windows filename/reserved-name, Unicode, concurrent serial, no-overwrite, failed-copy and cancelled-copy checks.
- Established flat-export media suite against the Windows adapters: Off without Auto-Editor, Off plus watermark, cached Noise plus Off, and ordinary preset cutting, with internal reports and source protection.
- Watermark pixel tests against Windows adapter: 0/25/100% opacity and transparent PNG alpha, output duration/audio and comparison metadata.
- Arabic Qt interface: scale migration/custom persistence; Off visibility; still-frame preview and dragging; export naming persistence; fresh-session watermark Off; shared video-only folder; Off+watermark, preset+cached Noise, Custom+cached Music; mapped playback and cooperative cancellation. Tested with macOS Qt 6.8.3, not Windows Qt binaries.
- Python source syntax checks. Retained Windows runtime files verified against the existing locked SHA-256 manifest; ZIP integrity and packaged source parity checked during packaging.

The new adapters retain Windows cooperative cancellation and child-tree handling, deep-filter.exe and the bundled music interpreter. They use explicit UTF-8 for reports containing Arabic paths. The Mac source and public VERSION remain unchanged. No extra runtime dependency is introduced.

## Required native follow-up

The Windows installer, Windows Qt playback/backend, actual taskkill child-tree behavior and fresh model execution were not run on this Mac. Medhat must test installation and the Arabic checklist in README_AR.html, including the long recording, before approval for a public Windows release. Existing installed tools/models/settings are reused; test outputs do not validate every codec, hardware configuration or external drive.

Local package hashes and verification results are recorded in the owner workspace work/windows151/VALIDATION.json. ZIP SHA-256 is also supplied beside the ZIP. This is an unsigned local test package, not a signed Windows publisher build.

## Owner test confirmation

After receiving the Windows 1.5.1_Test ZIP, the owner reported “done test passed”. Specific device, modes and recording duration were not supplied. This confirms owner acceptance while retaining the independent verification limits above. The tested ZIP and its checksum are unchanged; this documentation update does not rebuild or replace the package or authorize public publication.
