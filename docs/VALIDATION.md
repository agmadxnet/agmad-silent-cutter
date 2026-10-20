# Validation — 1.4.0 candidate, 20 October 2026

## Owner confirmation

On 20 October 2026 the owner reported checking both existing Mac and Windows versions and that both work well. This is user-reported acceptance of the 1.3 workflow on their devices. Detailed Windows OS/hardware, individual mode results and long-recording benchmarks were not supplied. It is not a claim of broad compatibility or native testing of the new 1.4.0 styling.

## Checks performed for 1.4.0

- Seven focused source/settings tests pass: exact Mac/Windows settings parity, original positive presets, balanced/gentlest behaviour, custom bounds and nonfinite rejection, and byte-level preservation of the 1.3 engine/setup adapters.
- Native arm64 Mac build succeeded. Signature structure verified with `codesign --verify --deep --strict` on the clean staging bundle. Build script signs outside the managed file-provider folder to avoid Finder metadata errors found during packaging. This is ad-hoc signing, not Apple notarization or Developer ID signing.
- Native Mac smoke checks passed for migration, preset/custom switching, reset clamping, field boundaries and timeline mapping. Native GUI integration rendered the synthetic 9-second fixture at level −1 to 6 seconds, loaded both players and advanced linked playback within the test tolerance.
- Arabic Qt/PySide interface, run on Mac, completed real Off, Noise, Music and Custom renders using an Arabic filename. Linked playback advanced; cooperative cancellation passed. This executes cross-platform source against Mac engines, not the Windows runtime.
- Arabic Custom layout fits a 1000×700 window after reducing spacing; minimum content size is checked to avoid hidden controls on a small laptop.
- Mac and Arabic Qt screenshots visually inspected. Corrected Mac primary-button contrast. Screenshots use anonymous demo labels/paths and synthetic media; they do not represent speech-quality benchmarks. Native video-layer images can be blank in view-cache captures even when playback positions advance.
- Product-page previews reviewed in English and Arabic in the browser. Local iframe audit at 320/390/768/1280px for both languages reported exactly one H1, correct LTR/RTL, two intentionally disabled download buttons and no horizontal document overflow. Original icon gradient and narrow-layout image sizing corrected during review.
- Website overlay is generated only for the existing Silent Cutter project templates/content and new scoped assets. The production site, MENA, newsletter and other tools were not changed.
- Prior 1.3 checks remain relevant: all eleven scale values rendered; known fixture durations -5…+5 were 9, 9, 7.866667, 7.833333, 6, 5.833333, 5.5, 5.166667, 4.833333, 4.666667 and 4.666667 seconds. Original SHA-256 remained unchanged. These engines are unchanged here.

## Release packaging checks

Windows retains the existing official CPython 3.13.16 / Qt/PySide/Shiboken 6.8.3 / pip 26.2.1 runtime. All retained runtime files are verified by SHA-256. Core/music setup locks and installer/data locations are unchanged. Runtime license texts/notices travel with the package. ZIP CRCs and final release SHA-256 are checked during packaging; exact artifacts are recorded in the adjacent RELEASE_MANIFEST.json / SHA256SUMS.

CI definitions are included but have not been run on GitHub yet. Local validation is not represented as remote CI success. Fresh native Windows installation, current new styling, Defender handling and setup downloads still need a final check on a Windows device. Fresh end-user Mac setup uses Homebrew's current formula, so its dependency version may differ from the existing tested installation; capture versions in support logs if setup differs.

## Remaining limits

No Intel Mac, Windows ARM/32-bit, physical phone website test, Windows VM, broad GPU/codec matrix, formal accessibility certification, security audit, signed publisher identity or Apple notarization. Real speech, accents, heavy music, wind, HDR and long lectures require practical output review. No new performance or speech-preservation guarantee is claimed. The website overlay still needs validation against current production bytes before deployment. Public source and the pre-release are now active: https://github.com/agmadxnet/agmad-silent-cutter/releases/tag/v1.4.0. Seven public release assets were re-downloaded and hash-verified. Production website rollout remains pending.
