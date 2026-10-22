# Website release — 1.4.0

Published 2026-10-20 as a public pre-release.

- English: https://agmad.net/projects/silent-cutter/
- Arabic: https://agmad.net/projects/silent-cutter/?lang=ar
- GitHub: https://github.com/agmadxnet/agmad-silent-cutter/releases/tag/v1.4.0

Seven narrowly scoped WordPress plugin files were updated: both product templates, the Silent Cutter record in content.js, and its badges in both home and project collection templates. PHP, other projects, newsletter and indexing policy were retained. Previous sources and deployment hashes are recorded in work/website-release/live-before and prepared/DEPLOYMENT.json in the owner workspace.

Verification: all seven saved editor sources matched the prepared files; both anonymous language pages returned HTTP 200 and correct download links; language switching, desktop layout, Arabic 390px phone layout and app screenshot decoding passed. Download assets had already been downloaded and checksum-verified against the reviewed release.

Limits: Mac is ad-hoc signed and not Apple-notarized; Windows has no publisher signature. The owner confirmed Medhat completed the requested Windows 1.4.0 test on 22 October 2026. Broad device testing remains open. The image server labels the AVIF preview as text/plain; the tested browser decoded it successfully. No global media or server configuration was changed.

Stable promotion approved by the owner on 22 October 2026 after Medhat’s Windows test. Existing tested installers, release tag, checksums and attached build-time records remain unchanged. Current documentation records later acceptance; attached source/validation/manifest files retain their historical build-time state.
