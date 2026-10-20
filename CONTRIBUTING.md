# Contributing

Keep changes focused. Run `python3 -m unittest discover -s tests -v`. For GUI changes, also build the Mac app or run the Windows Qt smoke test. Processing changes require an actual video render, stream/duration checks, original-file hash protection and listening to representative speech. Do not infer quality from synthetic tones alone.

Keep the platform settings modules byte-identical. Preserve source protection, cancellation, result timeline, settings identifiers and managed storage. Do not add telemetry, auto-updates, cloud processing or new dependencies without discussing the need.

Never commit recordings, cache, models, virtual environments, runtimes, private logs or credentials. See `.gitignore`. Binary installers are release assets. Record native-platform coverage honestly in docs/VALIDATION.md.
