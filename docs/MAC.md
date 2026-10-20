# Agmad Silent Cutter 1.4.0 — Mac installation

## Install or update

1. Quit the currently running Agmad Silent Cutter and Test apps.
2. Open the DMG. Drag **Agmad Silent Cutter.app** onto **Applications**.
3. If an older regular version is already installed, choose **Replace**.
4. Eject the DMG and open Agmad Silent Cutter from Applications, Spotlight, or the Dock.

The installed app stands alone: no companion source/tools folder needs to sit beside it. Keep any external v4 engine folder that you have selected until you deliberately switch to managed cleanup storage. After verifying this regular version, the separate Test app can be removed from Applications if you no longer need it. Removing the Test app is optional and is not performed by this package.

This is an Apple Silicon app for macOS 14+, tested on this Mac. It is locally/ad-hoc signed and not Apple Developer ID signed or notarized. If macOS blocks the downloaded app, use the approval for this specific app in System Settings → Privacy & Security after reviewing it; do not disable system security globally.

## Settings and existing cleanup tools

Version 1.4.0 preserves the same preference identifiers, data folders and processing as 1.3. Its visual update does not trigger a new settings import.

On the first 1.3 release launch, saved Test 1.3 settings are imported where available: scale/custom selection, exact scale level, custom numbers, cleanup choice, output destination and tool-folder connection. If Test 1.3 settings are absent, Test 1.2 settings are mapped to equivalent scale levels. Existing regular-app preferences remain available as the fallback.

This import happens once. Later changes made in the regular app remain yours and are not overwritten from the Test app on subsequent launches.

Your installed engines, models and cache are reused. If cleanup tools are already connected, you do not need to reinstall them. Otherwise use **Use existing v4 setup…**, or **Install cleanup tools…** for a managed installation. Initial installation requires Homebrew and internet; normal processing uses local audio/video files.

## Cutting controls

Choose **Preset scale** or **Custom**.

- **−5** is the gentlest setting.
- **0** is Balanced and still removes pauses; it is not an Off switch.
- **+1 through +5** preserve the original Standard 1–5 exactly.
- **Custom** offers guided numeric values with validation and Reset to preset.

| Level | Threshold | Padding per side | Minimum cut / speech clip |
|---|---|---|---|
| −5 | 0.5% | 0.50s | 1.50 / 0.15s |
| −4 | 0.75% | 0.40s | 1.20 / 0.15s |
| −3 | 1% | 0.35s | 1.00 / 0.15s |
| −2 | 1.5% | 0.325s | 0.90 / 0.15s |
| −1 | 2% | 0.30s | 0.80 / 0.15s |
| 0 | 4% | 0.25s | 0.60 / 0.15s |
| +1 | 8% | 0.20s | 0.45 / 0.15s |
| +2 | 12% | 0.12s | 0.25 / 0.12s |
| +3 | 20% | 0.06s | 0.15 / 0.08s |
| +4 | 30% | 0.04s | 0.10 / 0.06s |
| +5 | 40% | 0.02s | 0.08 / 0.05s |

Custom limits: threshold 0.5–40%, padding 0.02–0.60 seconds, and minimum pause 0.10–2.0 seconds. Lower threshold preserves quieter words; more padding protects word edges; a higher minimum pause retains shorter natural pauses. Use a decimal point and up to three decimal places.

Custom uses a fixed 0.15-second minimum speech clip. Reset loads the selected scale level's three displayed values within Custom limits; +5's 0.08-second minimum pause becomes 0.10. Select the scale level directly to reproduce its full smoothing settings exactly.

Threshold refers to full-scale audio amplitude, not the recording's own loudest point. Padding and smoothing interact. These presets do not guarantee a different result for every adjacent level, or preservation of every spoken word.

## Daily workflow

Choose or drop a video, choose the output destination, choose a scale level or Custom, choose Noise/Music/Off, then process. Start with 0 and a 30-second test. If quiet speech disappears, move toward −1, −3, or −5. The existing 30/60-second excerpt tests and start-time field remain available.

After rendering, use the edited player's controls for linked before/after playback. The original follows the corresponding source positions across cuts. Select which side's audio to hear, or disable linking to inspect original pauses independently.

Noise cleanup uses DeepFilterNet. Music cleanup uses the installed local UVR vocal model. Cleanup replaces the final soundtrack with cleaned mono speech from the first audio track; it can leave artifacts and cannot reliably recover speech obscured by severe distortion. Real speech quality and lip sync still need review.

## Files and storage

- Originals are never edited, moved, or overwritten.
- Every result gets a unique folder in your chosen destination, with MP4, PROCESS.log, SUMMARY.txt and comparison.json.
- Managed engines/models, setup logs and CACHE live in `~/Library/Application Support/Agmad Silent Cutter`.
- If an external v4 tools folder remains selected, its engines/cache stay there instead.
- New users default to `~/Movies/Agmad Silent Cutter`; imported/custom destinations take precedence.
- The app does not write processing files inside its signed bundle or Applications.

The app can stay in Applications permanently and be moved independently of its download folder. Homebrew dependencies and any selected external engine folder must continue to exist. Updating the app does not delete outputs or cache. No batch queue, new model, or new audio-processing feature is introduced by this packaging update.

## Source and credits

A separate source ZIP includes the buildable macos/Source/ project. The original silver waveform icon is described in branding/README.md in the source repository. Processing uses Auto-Editor (https://auto-editor.com), DeepFilterNet (https://github.com/Rikorose/DeepFilterNet), Audio Separator (https://github.com/nomadkaraoke/python-audio-separator), and UVR/MDX contributions (https://github.com/Anjok07/ultimatevocalremovergui). Downloaded components retain their own licenses. No models, Python environment, or test recordings are redistributed in this app bundle.

See VALIDATION.md for the release checks and remaining limits.
