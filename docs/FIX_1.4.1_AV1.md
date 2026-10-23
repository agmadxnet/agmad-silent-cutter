# Mac 1.4.1 test build: AV1 cleanup compatibility

The local PROCESS.log from the reported full-source failure states `av1 only supported in MP4 and AVIF` at MOV header creation. Cleanup stream-copied AV1 video into prepared.mov with PCM audio. The excerpt path first converts video to H.264, explaining why a short test could succeed for the same source. Duration was not the cause of this header failure.

Both platform engine copies now prepare Matroska video with lossless FLAC audio. Copying video avoids an extra lossy video pass. Matroska/PCM was tested first but exposed an AAC encoder/channel-layout failure in Auto-Editor; FLAC preserves the audio losslessly with suitable layout metadata and passes final export. Final public output remains H.264/AAC MP4.

Ten source/media tests passed, including AV1 Noise-cache, AV1 Music-cache and H.264 Noise-cache paths, decoded media, unchanged source/copied-video hashes, Auto-Editor timelines, and rendered duration within 150 ms of the timeline. These synthetic cached-audio tests isolate muxing; they do not benchmark cleanup quality. The historical 1.3 hash baseline is retained, with only this exact reviewed container/codec correction normalized for comparison. Native Mac build/signature and isolated smoke checks passed. Windows code parity is updated but no new Windows runtime build was tested or released.

A separate Mac 1.4.1 test app is packaged in the owner workspace. The exact reported external-volume recording was unavailable, so a full rerun of that file remains necessary. No public release, tag, website or installed application was replaced.

The owner subsequently reported the original 87-minute recording passed with the 1.4.1 test build. This is user-reported confirmation on that recording, not broader codec/device certification. The same fix is retained in the Mac watermark test build.
