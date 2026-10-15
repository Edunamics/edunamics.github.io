# Manufacturing and Statics formula / diagram rendering

The current scope is Manufacturing chapters 1–9 and Statics chapters 1–2.

1. Run `python tools/render-course-formulas.py` to rebuild 38 display SVG files
   and embedded inline/worked-example formula images from the preserved HTML
   in `course-formula-source.json` and reviewed TeX in `course-formula-data.py`.
2. Run `python tools/layout-course-diagrams.py` to outline all diagram labels,
   separate them from drawing edges and other labels, and retain longer moves
   with thin leaders. The report is written to the workspace output directory.

Requires Python, matplotlib, lxml, numpy, fonttools, and svgpathtools. The
renderer uses the macOS Arial Unicode font for Chinese labels; adapt the font
path in the utilities and layout script on another OS.

All formula and diagram glyphs are SVG paths, so the published result does not
need a math font or a client-side typesetter. Formula images retain alternative
text; diagram groups retain their original labels. Shared CSS supports phone
widths, dark/light themes, and printing. Edit the source snapshots and TeX,
then run both steps; do not edit base64 image data by hand.

Validation: all eleven chapters and expanded exam answers checked at 390px;
182 labeled diagrams / 1,115 labels; 77 moved labels; no remaining label/edge,
label/label, or leader/label intersections. Chinese prose and diagram labels
were checked against the source snapshot for preservation.
