# Al-Anbari Jewelry — Smart System Proposal (Aivora Studio)

Arabic RTL proposal PDF generated with WeasyPrint.

```bash
pip install weasyprint pymupdf fonttools brotli
./fetch_fonts.sh [SF-Arabic.dmg]   # SF Arabic (from Apple DMG or npm) + Cormorant (not committed)
python3 build.py        # -> output/Al-Anbari-Proposal-Aivora.pdf + output/preview/*.png
```

Edit Aivora contact details in the `AIVORA` dict at the top of `build.py`.
Product images in `assets/` are cropped from the store's Instagram screenshot.

## Animated video (9:16, 47s)

```bash
./fetch_fonts.sh
FFMPEG=/path/to/ffmpeg node video/render.mjs     # -> output/Al-Anbari-System-Video.mp4
node video/render.mjs --stills 3,20,38           # preview frames
```
`video/scene.html` holds the whole animation as a deterministic `render(t)` timeline.
