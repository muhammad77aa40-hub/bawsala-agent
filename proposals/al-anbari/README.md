# Al-Anbari Jewelry — Smart System Proposal (Aivora Studio)

Arabic RTL proposal PDF generated with WeasyPrint.

```bash
pip install weasyprint pymupdf fonttools brotli
./fetch_fonts.sh [SF-Arabic.dmg]   # SF Arabic (from Apple DMG or npm) + Cormorant (not committed)
python3 build.py        # -> output/Al-Anbari-Proposal-Aivora.pdf + output/preview/*.png
```

Edit Aivora contact details in the `AIVORA` dict at the top of `build.py`.
Product images in `assets/` are cropped from the store's Instagram screenshot.
