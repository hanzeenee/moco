# NEXON Lv.1 Gothic

The unmodified Bold face from the official low-size edition of NEXON Lv.1 Gothic is retained here. The current EA button displays the owner-supplied artwork to preserve its exact lettering; this font is no longer loaded by that button. Other site text keeps its existing font.

Official source: https://brand.nexon.com/ko/ci-brand-guidelines/typeface#section-lv1-gothic
Archive: https://brand.nexon.com/resources/NEXON_Lv1_Gothic.zip
Original archive entry: NEXON Lv1 Gothic Low_OTF/NEXON Lv1 Gothic Low OTF Bold.otf

NEXON's typeface FAQ permits commercial use and redistribution. It prohibits redistributing edited font files. This original OTF is included unchanged. Copyright remains with NEXON.

# Original icon font subset

`moconix-icons.woff2` retains the original Material Design Icons 5.9.55 glyphs,
Unicode values, metrics, contours and hinting. It includes all explicit app icons
(including dynamic class literals) and Vuetify default icons. `icons.css` keeps
the original pseudo-element layout, size, rotation, flip and spin rules.
The original package remains installed and its license is included here.

Normal builds run `node scripts/check-icon-subset.cjs` before bundling. The check
fails when source/Vuetify icon coverage changes, preventing missing icons from
being deployed. When intentionally adding an icon, regenerate from `frontend/`:

```sh
python -m pip install 'fonttools[woff]==4.68.0'
python scripts/subset-icons.py
```

The Python dependency is only for regenerating the committed subset; server
builds require no extra packages or network font conversion. Regeneration
verifies the exact contours, advance metrics and hinting for every glyph.

Roboto continues to use the exact same Google Fonts stylesheet, weights and
`display=swap` setting. Its link now appears once in the shared document head,
with early connections to the two font origins, rather than being requested
again through a JavaScript webfont-loader chunk.
