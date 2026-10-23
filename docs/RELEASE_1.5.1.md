# AGMAD Silent Cutter 1.5.1 — proposed release

Status: prepared for owner review; not published. Public release remains 1.4.0.

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

## Proposed publication scope

1. Publish only the reviewed source snapshot to agmadxnet/agmad-silent-cutter and create v1.5.1 against the verified matching source commit. Do not move the existing v1.4.0 tag.
2. Upload the exact reviewed Mac DMG/ZIP, Windows ZIP, source ZIP, release notes, validation, manifest and SHA256SUMS. Set 1.5.1 as the latest stable release only with owner approval.
3. Re-download and hash every public asset before enabling the corresponding website links. Proposed URLs in the preparation bundle are unverified until then.
4. Fetch current production files, then update only the existing English/Arabic Silent Cutter product pages, their download/version metadata and existing project badge if needed. Preserve navigation, other products, the journal article and current indexing policy. Do not deploy a historical full-site snapshot.
5. Retain 1.4.0 installers, release/tag and a fresh backup of changed live page files. Rollback points the product-page downloads back to 1.4.0; it does not remove user settings, engines, models or outputs.

No GitHub or WordPress mutation is authorized by preparation alone. Review bundle: outputs/Agmad_Silent_Cutter_Release_1.5.1_Review in the owner workspace.
