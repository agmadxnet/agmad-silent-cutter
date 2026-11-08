# Build and package

Use Python 3.12+ for source checks/build scripts. No engine or media is needed for `python3 -m unittest discover -s tests -v`.

## Mac

On Apple Silicon macOS 14+ with Xcode command-line tools:

```sh
bash macos/Source/build.command
```

The app appears at `macos/Agmad Silent Cutter.app`. The script compiles arm64, copies the helper payload and icon, removes resource metadata, and ad-hoc signs the bundle. It does not install it in Applications, download models or notarize it. `codesign --verify --deep --strict` checks signature structure, not publisher trust.

For smoke/integration tests, launch the executable with `--smoke-test` or `--integration-test`; these use an isolated preferences suite. Set AGMAD_TEST_DATA, CUTTER_INPUT, CUTTER_ENGINE, CUTTER_DEST and CUTTER_SCREENSHOT to dedicated test paths. Integration needs already installed tools and a test video. Do not point test outputs at originals.

Run `bash scripts/package_macos.sh /fresh/output/folder` to build and verify a DMG and ZIP. The script creates a DMG from a fresh staging directory containing the app, README.md, VALIDATION.md, LICENSE and an Applications symlink. Keep source outside the app. The archive and DMG are locally signed only; Developer ID signing/notarization requires the owner's Apple developer setup and is not part of this build.

## Windows

```sh
python3 scripts/package_windows.py --output ../release-build
```

The packager uses locked official CPython and PySide/Shiboken/pip downloads, verifies SHA-256, prunes to the recorded runtime manifest and checks the retained files. `build-info.json` records upstream provenance, `runtime-sha256.json` records expected retained files. It can run on Mac to assemble Windows binaries, but this does not execute or test them.

For an already verified runtime:

```sh
python3 scripts/package_windows.py --output ../release-build --runtime /path/to/existing/runtime
```

The runtime is checked against the manifest before packaging. The app, icons, setup metadata, original runtime notices, license texts and Arabic instructions ship together. The shortcut launches pythonw.exe with readable app source; no new freezing dependency is needed.

Windows core engine downloads and optional CPU music dependencies remain pinned separately in assets/downloads.json and assets/music-requirements.txt. Mac optional requirements remain in its payload; do not swap these platform-specific lists. Setup is an explicit user action.

## Replace or inspect Qt

Qt is dynamically linked and not embedded into an opaque executable. Preserve notices; rebuild with appropriate compatible libraries under their terms if replacing it. Native runtime files are unmodified official wheel members. The LGPL/GPL texts and source locations are in windows/LICENSES and THIRD_PARTY_NOTICES.md. The manifest deliberately rejects unexpected bytes during a release build; update it intentionally for a documented dependency update, not by disabling the check.

## Icons

Run `python3 scripts/make_icons.py` with Pillow installed. Mac additionally uses iconutil. SVG and rendered artwork are original code-created assets. Icons are already checked into source; Pillow is not an app runtime dependency.

## Release checksums

Generate SHA256SUMS for the final ZIP/DMG/source artifacts, verify ZIP CRCs, and record file sizes/hashes in the release manifest. Do not rebuild after approving those hashes without repeating approval. Do not commit runtimes, installed environments, models, recordings or logs to Git.

## Historical Windows 1.5.1 candidate

Keep public VERSION unchanged. Package the port with the existing verified runtime and candidate-specific Arabic instructions/validation:

```sh
python3 scripts/package_windows.py --output /fresh/output/folder --runtime /path/to/verified/runtime --version 1.5.1_Test --readme docs/WINDOWS_1.5.1_TEST.ar.md --validation docs/WINDOWS_1.5.1_VALIDATION.md
```

Optional --version/--readme/--validation leave the default stable packaging workflow intact. Package build-info records the selected candidate version while retaining the upstream runtime provenance. Native Windows installation/playback and cleanup validation remain required before public release.

## Documentation checks for future packages

Build from a reviewed checkout containing the cleaned documentation. Mac packages use `docs/PACKAGE_MAC.md`; Windows packages use `docs/PACKAGE_WINDOWS.ar.md` and generate both Markdown and HTML from that one source. The older version-specific guides remain historical records. Custom Windows `--readme` and `--validation` inputs are checked before runtime downloads or output staging. Both packagers check staged documentation and the completed ZIP; the Mac DMG uses the same checked staging folder.

The read-only documentation gate blocks the targeted personal attribution and private home/workspace references. It never redacts files, changes licenses, or edits existing releases. If required third-party attribution triggers a check, review the licensing requirement; do not remove legally required credits. This targeted check is not a general secret scanner or a substitute for human review. Standard per-user application storage paths and generic build placeholders remain documented.

Run the same check on any additional release notes, manifests, website bundles or custom package documents before distributing them:

```sh
python3 scripts/check_release_docs.py README.md README.ar.md STATUS.md CHANGELOG.md docs website
python3 scripts/check_release_docs.py /path/to/new/package.zip /path/to/new/release-notes.md
```

Create future source packages with:

```sh
python3 scripts/package_source.py --output /fresh/output/folder
```

This uses the resolved HEAD commit and that commit's VERSION, preserves tracked source/licenses, checks the archive's documentation and writes a new ZIP plus SHA-256 file. Uncommitted files are not included. Commit and review intended documentation updates first; verify the printed commit before release. Existing filenames are refused rather than replaced. Manually assembled archives must pass the same documentation gate.

For a new release, update and review the guides and dated validation evidence for that version. Historical acceptance does not validate a newly built installer. Never rebuild, replace or delete existing published assets or move tags as part of documentation maintenance.
