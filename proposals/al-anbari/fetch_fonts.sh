#!/usr/bin/env bash
# Prepares SF Arabic + Cormorant Garamond and creates static SF Arabic weights for WeasyPrint.
# Usage: ./fetch_fonts.sh [path/to/SF-Arabic.dmg]
#   with a DMG: SF Arabic is taken from Apple's installer (needs 7z)
#   without:    SF Arabic is downloaded from npm (@fontpkg/sf-arabic, identical file)
set -e
DMG="${1:+$(realpath "$1")}"
cd "$(dirname "$0")"; mkdir -p fonts .tmp && cd .tmp
npm pack @fontsource/cormorant-garamond >/dev/null
if [ -n "$DMG" ]; then
  mkdir -p fontpkg-sf-arabic-dmg && 7z x -y -odmg "$DMG" >/dev/null
  7z x -y -opkg "$(find dmg -name '*.pkg' | head -1)" >/dev/null
  7z x -y -opayload "$(find pkg -name 'Payload*' | head -1)" >/dev/null
  cp "$(find payload -name 'SF-Arabic.ttf' | head -1)" fontpkg-sf-arabic-dmg/
else
  npm pack @fontpkg/sf-arabic >/dev/null
fi
for f in *.tgz; do tar xzf "$f" && mv package "${f%.tgz}"; done
cp fontsource-cormorant-garamond-*/files/cormorant-garamond-latin-{300,400,500,600,700}-normal.woff ../fonts/
cp fontsource-cormorant-garamond-*/files/cormorant-garamond-latin-{400,500}-italic.woff ../fonts/
python3 - <<'PY'
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import glob
src = glob.glob('fontpkg-sf-arabic-*/SF-Arabic.ttf')[0]
for name, w in [('Light',300),('Regular',400),('Medium',510),('Semibold',620),('Bold',711),('Heavy',844)]:
    f = TTFont(src); instantiateVariableFont(f, {'wght': w, 'opsz': 28}, inplace=True); f.save(f'../fonts/SFArabic-{name}.ttf')
PY
cd .. && rm -rf .tmp && echo "fonts ready"
