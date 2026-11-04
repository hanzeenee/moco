# MOCONIX brand assets

Original PNGs supplied by the owner on 2026-10-27. Files are preserved without pixel edits.

| Project asset | Original filename | Usage |
| --- | --- | --- |
| moconix-wordmark.png | 누끼_전체.png | Header wordmark (white letters and gold symbol). Despite its source name, this PNG contains an opaque black background and outer margins. The header frames those margins in CSS. |
| moconix-mark-transparent.png | 누끼_로고.png | Gold symbol with transparency; used in the EA simulator terminal title bar. |
| moconix-mark-on-white.png | 로고_백.png | Symbol variant supplied for a white background. |
| moconix-mark-on-black.png | 로고_흑.png | Symbol variant supplied for a black background. |
| moconix-wordmark-on-white.png | 로고전체_배경흰색.png | Full wordmark variant supplied for a white background. |
| moconix-wordmark-on-black.png | 로고전체_배경검정.png | Full wordmark variant supplied for a black background. |

The header wordmark and simulator terminal symbol are imported into the application. Keep the other originals for later owner-directed placements.

Favicon assets in frontend/public are derived from moconix-mark-transparent.png (누끼_로고.png). At the owner's request, the favicon uses the original symbol aspect ratio with zero added padding and fills the complete canvas width. The symbol is centered vertically with natural transparent space above and below. Original brand files and the header wordmark remain unchanged. favicon.ico contains 16/32/48/64px frames; 32px and 64px PNG alternatives are linked explicitly. All icon URLs include a version suffix to refresh the previous favicon cache.


## Lossless delivery variants

The original PNG files above remain unchanged. The site uses smaller, full-resolution
`.webp` delivery variants for referenced brand images when lossless WebP saves bytes.
No images were resized, cropped, redrawn, or encoded with lossy compression.
Decoded alpha and every RGB channel with nonzero alpha were compared against each
PNG; all matched exactly. Some fully transparent pixels may have different hidden
RGB values after WebP encoding, which does not change their displayed color.
CSS framing, masks, scale factors, and layout are unchanged. Keep the original PNGs
for future source work; do not replace them with the delivery variants.

## Responsive delivery sizes

`responsive/` contains additional, smaller WebP candidates for high-density
`srcset` selection. Full-resolution PNG/WebP originals, all favicon files, the EA
button artwork and Gmail artwork remain byte-for-byte unchanged. Each image's
entire original canvas is resized with Lanczos3; there is no crop, trim, redraw,
sharpening or recoloring. The selected dimensions deliberately provide generous
resolution for the current CSS display sizes (including the utility icon's
existing scale transform). INFINOX uses the more generous 128/256/384/512px
candidates to preserve its small white-circle and gold detail. Original full-resolution WebP files remain the `src`
fallback and highest-density `srcset` candidates.

Unlike the full-resolution variants above, responsive images are intentionally
resampled. WebP encoding is lossless relative to the resized pixels: decoded
alpha and visible RGB are verified exactly against the raw resized buffer.
The header wordmark uses its original 1983/793 CSS aspect ratio because integer
resizing rounds its candidate heights. No existing framing or mask is changed.

Regenerate only when source artwork or requested display sizes change:

```sh
# Optional local tool; not a production build/runtime dependency.
# Tested/pinned Sharp 0.33.2 (libvips 8.15.1, libwebp 1.3.2).
# MOCONIX_SHARP_MODULE may point to an existing Sharp installation.
node scripts/generate-responsive-brand.cjs --report-dir /absolute/artifact/path
```

The generator preserves and verifies SHA-256 hashes for every existing brand
image and favicon. It writes only the responsive directory and, when requested,
a verification report at the supplied artifact path. Committed responsive
assets require no Sharp installation or regeneration during deployment builds.
