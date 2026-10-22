# agmad.net integration — deployed 20 October 2026

The live product pages are https://agmad.net/projects/silent-cutter/ and https://agmad.net/projects/silent-cutter/?lang=ar. Both serve verified 1.4.0 pre-release download links. See [deployment scope and validation](../docs/WEBSITE_RELEASE.md).

The instructions below describe the preparation procedure for future updates; fetch current production files before using the historical overlay script.

`index.html` / `index.ar.html` are local noindex previews. `section.en.html` / `section.ar.html` are content fragments for the existing project route. CSS is scoped to `.cutter` to preserve the site's navigation, newsletter and other products. Icon artwork is original; screenshots show the actual app. There are no external scripts, fonts, forms, analytics, model requests or file uploads in the preview.

Run `scripts/prepare_site_overlay.py --studio /path/to/reviewed/agmad-studio-v3 --output /new/review-overlay`. It prepares only the two existing project templates, a narrowly updated project record in content.js and new cutter assets. It injects the existing `AGMAD_SERVER_PAGE` convention so the Studio runtime preserves server-rendered product content. It does not overwrite files in place or deploy anything.

Before applying, fetch the CURRENT production templates/content/runtime and diff against the reviewed snapshot. Do not upload the whole source project or overwrite newer editorial records. Confirm the live runtime still honours AGMAD_SERVER_PAGE. Keep existing canonical/hreflang and noindex until the release is actually available. Existing clean URLs/header/footer and EN/AR switch stay under Studio ownership. No MENA/scanner, subscription or other tools state changes are authorized by this overlay.

## Enable downloads after release approval

1. Create/confirm the selected GitHub repository and publish reviewed source and release assets.
2. Verify public asset URLs, sizes and SHA-256 against the release manifest. Download and verify at least one asset per platform; do not use guessed links.
3. Fill `release.json` with actual HTTPS URLs and mark published only after the GitHub release is visible.
4. Replace the disabled download buttons in BOTH fragments with the verified direct release links. Add source and checksum links, minimum requirements and signing disclosures next to them. Remove the preview-only notice only after owner approval.
5. Regenerate/review the two template overlays and project record. The public source repository is `agmadxnet/agmad-silent-cutter`.
6. Apply only approved files to the existing Studio plugin. Review EN/AR at phone and desktop widths, navigation, downloads, canonical/hreflang, robots and the homepage project status. Then explicitly approve indexing updates for this project page; do not change global sitemap/indexing policy.

Do not replace disabled links with local filesystem paths or invent a download counter, testimonial or signing claim. The public app remains free of a required account; there is no subscription/entitlement change.

## Stable promotion

Owner approved on 22 October 2026 following Medhat’s Windows test. Current fragments/release.json describe stable 1.4.0. Keep the existing indexing policy and all download files unchanged.
