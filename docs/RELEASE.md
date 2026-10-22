# Release preparation — 1.4.0

Public repository and pre-release approved and published on 20 October 2026:

- https://github.com/agmadxnet/agmad-silent-cutter
- https://github.com/agmadxnet/agmad-silent-cutter/releases/tag/v1.4.0

All 78 source files matched the reviewed local Git blobs before tagging. Seven public release downloads matched approved SHA-256 values. The browser session was used because connector/CLI write access was unavailable. The checklist below remains the release procedure; public GitHub steps are complete, and the bilingual production website rollout completed on 20 October 2026. Native Windows visual confirmation remains pending. See [website deployment](WEBSITE_RELEASE.md).

## Prepared

- Source-only project with English/Arabic documentation, MIT application license, dependency notices, original icons and screenshots.
- Working scale/custom/cleanup pipeline retained from the owner-tested 1.3 release.
- Mac Apple Silicon app/DMG/ZIP and Windows x64 ZIP, with checksums/manifest.
- Source archive for GitHub. Runtime/model/media/cache/logs are not committed to source.
- CI definitions, issue/PR templates, build scripts and focused regression tests.
- Bilingual noindex website preview and narrowly scoped Studio integration overlay.

## Final review before sharing

1. Review the visual change and prepared MIT source license. Confirm the repository owner/name and whether source should be public; third-party licenses remain independent.
2. Test a short normal recording with the styled Mac and Windows packages. The owner already accepted the 1.3 workflow; a new Windows visual/native check is still needed after styling.
3. Review version, minimum OS, optional download sizes/signing disclosures, LICENSES and source links. No Developer ID, notarization or Windows publisher signature is claimed. If a signed mainstream distribution is required, complete the owner's signing setup before release.
4. Freeze exact artifact SHA-256 and file sizes from RELEASE_MANIFEST.json. Upload only those installers, source archive and SHA256SUMS; never upload the workspace or installed environments/models.
5. Publish the reviewed repository and a GitHub release. Use the app source tag `v1.4.0` only for the reviewed commit; do not assume locally built artifacts are automatically reproducible bit-for-bit.
6. Verify public release/source URLs and re-download/hash the assets. CI must actually run before claiming a green build.
7. Fill website/release.json with the verified URLs and enable BOTH localized download links. Review/apply only the existing project route overlay, then check downloads, language navigation, canonical/hreflang and robots. Do not deploy an old full Studio snapshot over current editorial work.
8. Update candidate wording/indexing only after the downloads are live and explicit publication approval is given. Keep other products' release states unchanged.

Rollback: retain previous 1.3 DMG/ZIP and the pre-deployment project templates/content. Replacing the app or restoring the page does not delete result folders or managed engines. Do not remove existing user settings/cache as part of rollback.

## GitHub checks reviewed 22 October 2026

[Latest reviewed run](https://github.com/agmadxnet/agmad-silent-cutter/actions/runs/39464427700): source regression tests and native Mac build/signature verification passed. The Windows job was cancelled before execution because GitHub could not acquire a hosted runner. This is not a passed Windows check; rerun it when runner capacity is available. No installer or release tag was changed.
