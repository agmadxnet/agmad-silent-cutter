# Troubleshooting

**Little or no cutting:** background music/noise may exceed the threshold throughout the clip. Try a short excerpt with Noise or Music, then increase the level gradually. Check the log, SUMMARY.txt and removed percentage. Do not jump to +5 if quiet speech matters.

**Quiet words cut:** lower the level. In Custom, lower threshold, increase padding, or increase minimum pause. Compare to the original using a short test.

**No output:** open the current log. Confirm setup completed, the source exists, the destination is writable and disk space is sufficient. Cancellation intentionally removes incomplete output. Do not rename a partial file as a finished result.

**Music mode fails:** complete optional setup first; core setup alone is insufficient. Music libraries/models are large and require more time, memory and disk. On an 8GB laptop, close other applications and test 30 seconds. Existing cached audio can make repeated tests faster.

**Preview blank or unsupported:** open the completed MP4 in an external player; this distinguishes preview/codec errors from rendering failures. Record Windows version, app version, GPU if known, and redacted error text.

**Windows app does not start:** extract the entire ZIP; quit the old app; run Install.cmd. Check `%LOCALAPPDATA%\Agmad Silent Cutter\LOGS\launch.log`. Keep DLLs and runtime files with the app. If a Microsoft runtime prompt appears, use the official provider route. Do not disable protection globally.

**Mac blocks the download:** the candidate is ad-hoc signed, not notarized. Use the specific app approval in System Settings → Privacy & Security if you trust the reviewed download. Do not disable Gatekeeper globally. The build targets Apple Silicon macOS 14+, not Intel Macs.

**Update:** quit the old version; replace the Mac app in Applications or run the new Windows Install.cmd. Managed tools/models and previous outputs remain separate. Keep the previous ZIP/DMG for rollback. Reverting a binary does not delete your results.

Please include app/OS version, selected level/custom values, cleanup option, excerpt scope, error text and reproducible steps. Do not post private media or unredacted local paths.
