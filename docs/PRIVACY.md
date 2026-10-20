# Privacy

The desktop processing pipeline does not upload your video or audio to a processing service. No analytics, account system, telemetry or automatic crash-report sender is implemented in the app. The website and GitHub have their own privacy behaviour; this statement covers the desktop application.

Internet is needed for explicit setup/download actions: Homebrew on Mac; official processing tools; optional music packages and model metadata/weights; and Microsoft's runtime fallback if required on Windows. Those hosts receive normal network request information. Once dependencies are installed, processing uses local files. No automatic app updater is included.

Outputs, temporary media and cleaned-audio cache occupy local disk. Logs and comparison.json can contain full paths, filenames, durations and commands. Closing the app does not erase completed outputs/cache/logs. Use the documented storage paths to remove them when no job is running; keep any results you need. Deleted local files are not guaranteed securely erased.

For support, share the smallest relevant error text and remove personal paths, filenames and media. Do not attach private recordings or complete unredacted logs to public GitHub issues. Keep backup originals and review outputs before publication.
