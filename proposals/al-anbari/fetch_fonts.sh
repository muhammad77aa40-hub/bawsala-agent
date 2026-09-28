#!/usr/bin/env bash
# Downloads SF Arabic + Cormorant Garamond from npm and creates static SF Arabic weights for WeasyPrint.
set -e
cd "$(dirname "$0")"; mkdir -p fonts .tmp && cd .tmp
npm pack @fontpkg/sf-arabic @fontsource/cormorant-garamond >/dev/null
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
