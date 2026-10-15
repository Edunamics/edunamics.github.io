# Dynamics formula images

`render-dynamics-formulas.py` builds the 63 display SVGs in
`assets/dynamics-formulas/` and embeds inline/worked-example SVG images in all
seven Dynamics chapters. Every glyph is a path, so viewing requires no math
font, JavaScript typesetter, or external service. The CSS supports light/dark
mode, responsive scaling, and printing. Every image has alternative text.

`dynamics-formula-data.py` holds reviewed display TeX and explanatory notes.
`dynamics-formula-source.json` preserves the pre-render HTML for repeatable
builds. Edit the source snapshot to change prose or worked examples; edit the
TeX data to change a display equation. Do not edit base64 image data by hand.

Requires Python, matplotlib, and lxml. The Chinese note font is Arial Unicode
at the macOS system font location specified by `CJK` in the renderer; adapt that
path on another OS. Run `python tools/render-dynamics-formulas.py` from the repo.

The conversion repairs an unclosed subscript in the downward-throw paragraph
and corrects the centripetal-force period expression to `4π²mr/T²`.
