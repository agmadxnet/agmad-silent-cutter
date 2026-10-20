#!/bin/bash
set -e
cd "$(dirname "$0")/.."
build_root="$(mktemp -d /tmp/agmad-cutter-build.XXXXXX)"
trap 'rm -rf "$build_root"' EXIT
app="$build_root/Agmad Silent Cutter.app"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources"
cp -R Source/Payload/engine "$app/Contents/Resources/"
cp Source/AppIcon.icns "$app/Contents/Resources/AppIcon.icns"
xcrun swiftc -swift-version 5 -target arm64-apple-macos14.0 -O Source/App.swift -o "$app/Contents/MacOS/AgmadSilentCutter" -framework AppKit -framework AVKit -framework AVFoundation -framework UniformTypeIdentifiers
cat > "$app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>AgmadSilentCutter</string>
<key>CFBundleIdentifier</key><string>net.agmad.silentcutter</string>
<key>CFBundleName</key><string>Agmad Silent Cutter</string>
<key>CFBundleDisplayName</key><string>Agmad Silent Cutter</string>
<key>CFBundleIconFile</key><string>AppIcon</string>
<key>CFBundleVersion</key><string>6</string>
<key>CFBundleShortVersionString</key><string>1.4.0</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>LSMinimumSystemVersion</key><string>14.0</string>
<key>NSHighResolutionCapable</key><true/>
<key>NSHumanReadableCopyright</key><string>Agmad Silent Cutter. Third-party components retain their respective licenses.</string>
</dict></plist>
PLIST
find "$app/Contents/Resources" -name __pycache__ -type d -prune -exec rm -rf {} +
xattr -cr "$app"
codesign --force --sign - "$app"

codesign --verify --deep --strict "$app"
# File-provider folders may attach Finder metadata; sign outside them first.
output="${AGMAD_BUILD_OUTPUT:-$PWD/Agmad Silent Cutter.app}"
ditto --norsrc --noextattr --noqtn "$app" "$output"
printf 'Built: %s\n' "$output"
