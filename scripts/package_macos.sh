#!/bin/bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
output="${1:?Choose an output directory}"
mkdir -p "$output"
output="$(cd "$output" && pwd)"
version="$(cat "$root/VERSION")"
name="Agmad_Silent_Cutter_Mac_$version"
if [ -e "$output/$name.dmg" ] || [ -e "$output/$name.zip" ]; then
  echo 'Choose a fresh output directory; existing releases are preserved.' >&2
  exit 1
fi
stage="$(mktemp -d /tmp/agmad-cutter-release.XXXXXX)"
trap 'rm -rf "$stage"' EXIT
payload="$stage/$name"
mkdir -p "$payload"
AGMAD_BUILD_OUTPUT="$payload/Agmad Silent Cutter.app" bash "$root/macos/Source/build.command"
cp "$root/docs/MAC.md" "$payload/README.md"
cp "$root/docs/VALIDATION.md" "$payload/VALIDATION.md"
cp "$root/LICENSE" "$payload/LICENSE"
cp "$root/THIRD_PARTY_NOTICES.md" "$payload/THIRD_PARTY_NOTICES.md"
ln -s /Applications "$payload/Applications"
xattr -cr "$payload"
codesign --verify --deep --strict "$payload/Agmad Silent Cutter.app"
hdiutil create -volname 'AGMAD Silent Cutter' -fs HFS+ -srcfolder "$payload" -format UDZO "$output/$name.dmg"
hdiutil verify "$output/$name.dmg"
ditto -c -k --norsrc --noextattr --noqtn --keepParent "$payload" "$output/$name.zip"
printf 'Created: %s\n' "$output/$name.dmg" "$output/$name.zip"
