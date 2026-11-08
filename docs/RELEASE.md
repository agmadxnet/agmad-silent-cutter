# Release preparation — 1.4.0

> Historical record: preparation and test statements below describe their original stage, not current availability. Version [1.5.1 is published as a stable release](https://github.com/agmadxnet/agmad-silent-cutter/releases/tag/v1.5.1), verified 2026-11-08. Test results and untested areas remain as recorded; release assets and tags are unchanged.

Public repository and pre-release approved and published on 20 October 2026:

- https://github.com/agmadxnet/agmad-silent-cutter
- https://github.com/agmadxnet/agmad-silent-cutter/releases/tag/v1.4.0

All 78 source files matched the reviewed local Git blobs before tagging. Seven public release downloads matched approved SHA-256 values. The checks below summarize reproducible release verification; public GitHub steps are complete, and the bilingual production website rollout completed on 20 October 2026. The owner confirmed the Windows tester completed the requested Windows 1.4.0 test on 22 October 2026. See [website deployment](WEBSITE_RELEASE.md).

## Prepared

- Source-only project with English/Arabic documentation, MIT application license, dependency notices, original icons and screenshots.
- Working scale/custom/cleanup pipeline retained from the owner-tested 1.3 release.
- Mac Apple Silicon app/DMG/ZIP and Windows x64 ZIP, with checksums/manifest.
- Source archive for GitHub. Runtime/model/media/cache/logs are not committed to source.
- CI definitions, issue/PR templates, build scripts and focused regression tests.
- Bilingual noindex website preview and narrowly scoped Studio integration overlay.

## Reproducible release checks

- Preserve source and third-party license notices, signing disclosures, minimum OS and dependency requirements.
- Build using [BUILD.md](BUILD.md); do not assume independently built packages reproduce published binaries bit for bit.
- Record artifact SHA-256 and file sizes in a manifest. Verify downloaded assets against the published checksums.
- Run CI before claiming a passing build; distinguish source checks, native runtime tests and user-reported acceptance.
- Keep previous releases and user settings, engines, models and outputs intact when updating or rolling back.

## GitHub checks reviewed 22 October 2026

[Latest reviewed run](https://github.com/agmadxnet/agmad-silent-cutter/actions/runs/39464427700): source regression tests and native Mac build/signature verification passed. The Windows job was cancelled before execution because GitHub could not acquire a hosted runner. This is not a passed Windows check; rerun it when runner capacity is available. No installer or release tag was changed.

Stable promotion approved by the owner on 22 October 2026 after the native Windows test. Existing tested installers, release tag, checksums and attached build-time records remain unchanged. Current documentation records later acceptance; attached source/validation/manifest files retain their historical build-time state.
