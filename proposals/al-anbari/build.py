# -*- coding: utf-8 -*-
"""
Aivora Studio — عرض منظومة مجوهرات الأنباري الذكية
يولّد ملف PDF عربي RTL عبر WeasyPrint، ثم يحوّل كل صفحة لصورة PNG للمراجعة.

python3 build.py            -> output/Al-Anbari-Proposal-Aivora.pdf + output/preview/*.png
"""
import pathlib
from weasyprint import HTML

ROOT = pathlib.Path(__file__).parent
ASSETS = ROOT / "assets"
FONTS = ROOT / "fonts"
OUT = ROOT / "output"

# ------------------------------------------------------------------
# معلومات التواصل الخاصة بـ Aivora (عدّلها قبل الإرسال)
# ------------------------------------------------------------------
AIVORA = {
    "phone": "+964 750 000 0000",
    "email": "hello@aivora.studio",
    "web": "aivora.studio",
    "insta": "@aivora.studio",
    "city": "أربيل — إقليم كوردستان العراق",
}
STORE = {
    "name": "مجوهرات الأنباري",
    "en": "AL-ANBARI JEWELRY",
    "insta": "@gold_al_anbary",
    "address": "بغداد — زيونة، شارع الربيعي، مجمع الذهب",
}
DATE_AR = "أيلول 2026"


def a(name):
    return (ASSETS / name).as_uri()


# ------------------------------------------------------------------
# Icons — inline SVG, fill/stroke as attributes
# ------------------------------------------------------------------
ICONS = {
    "tag": '<path d="M3 12V4h8l10 10-8 8L3 12z"/><circle cx="7.5" cy="8" r="1.5"/>',
    "chat": '<path d="M4 5h16v11H9.5L4 20V5z"/><path d="M8 9.5h8M8 12.5h5"/>',
    "book": '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3V4z"/><path d="M5 17a3 3 0 0 1 3-3h11"/><path d="M9 8h6"/>',
    "scale": '<path d="M12 3v17M7.5 20.5h9M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0L5 7zM19 7l-3 6a3 3 0 0 0 6 0l-3-6z"/>',
    "ring": '<circle cx="12" cy="14.5" r="6"/><path d="M9 5.5l3-3 3 3-3 3z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "box": '<path d="M3 7.5l9-4.5 9 4.5v9L12 21l-9-4.5v-9z"/><path d="M3 7.5l9 4.5 9-4.5M12 12v9"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M17.5 14a6 6 0 0 1 4 6"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "chart": '<path d="M3 20.5h18M6 20V11M11 20V5M16 20v-7M20 20V9"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "spark": '<path d="M12 2.5l2.2 6.8 6.8 2.2-6.8 2.2L12 20.5l-2.2-6.8L3 11.5l6.8-2.2z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "truck": '<path d="M2 6h12v10H2zM14 9.5h4l3 3.5v3h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "bell": '<path d="M6 16v-5a6 6 0 0 1 12 0v5l2 2H4l2-2z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "phone": '<rect x="6.5" y="2" width="11" height="20" rx="2.5"/><path d="M10.5 18.5h3"/>',
    "monitor": '<rect x="2" y="4" width="20" height="13" rx="1.5"/><path d="M8 21h8M12 17v4"/>',
    "exchange": '<path d="M4 9a8 8 0 0 1 14-3.2L20 8"/><path d="M20 3.5V8h-4.5"/><path d="M20 15a8 8 0 0 1-14 3.2L4 16"/><path d="M4 20.5V16h4.5"/>',
    "receipt": '<path d="M6 2.5h12v19l-3-2-3 2-3-2-3 2v-19z"/><path d="M9 7.5h6M9 11h6M9 14.5h4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20.5 20.5l-4.5-4.5"/>',
    "whatsapp": '<path d="M4 20.5l1.4-4.2A8.5 8.5 0 1 1 8.2 19L4 20.5z"/><path d="M9 8.5c0 3.5 3 6.5 6.5 6.5l1-1.8-2-1-1 1c-1-.5-2.2-1.7-2.7-2.7l1-1-1-2L9 8.5z"/>',
    "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="6" rx="1"/><rect x="17" y="14" width="4" height="6" rx="1"/>',
    "pin": '<path d="M12 21.5s-7-6-7-11.5a7 7 0 0 1 14 0c0 5.5-7 11.5-7 11.5z"/><circle cx="12" cy="10" r="2.5"/>',
    "wallet": '<path d="M3 7.5h17v12.5H3z"/><path d="M3 7.5l12-4v4"/><path d="M15 13.5h5"/>',
    "flame": '<path d="M12 2.5c1 4 6 5.5 6 11a6 6 0 0 1-12 0c0-3 1.5-4.5 2.5-6.5 1 1.5 1.5 2.5 3 3.5.5-2.5.5-5 .5-8z"/>',
    "camera": '<rect x="3" y="7" width="18" height="13" rx="2"/><circle cx="12" cy="13.5" r="3.5"/><path d="M8.5 7l1.5-2.5h4L15.5 7"/>',
    "bot": '<rect x="4.5" y="8" width="15" height="11" rx="3"/><path d="M12 4v4M2.5 13v2M21.5 13v2"/><circle cx="9.3" cy="13.5" r="1.2"/><circle cx="14.7" cy="13.5" r="1.2"/>',
    "layers": '<path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5"/><path d="M3 16.5l9 4.5 9-4.5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
    "gem": '<path d="M6.5 3.5h11l4 5.5L12 21 2.5 9z"/><path d="M2.5 9h19M12 21L8.5 9l2-5.5M12 21l3.5-12-2-5.5"/>',
    "insta": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="0.6"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
    "barcode": '<path d="M4 5v14M7 5v14M10 5v14M14 5v14M16 5v14M20 5v14"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.3"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M13.5 4.5l-3 15"/>',
    "pen": '<path d="M4 20l1-4.5L16 4.5l3.5 3.5L8.5 19z"/><path d="M13.5 7.5l3 3"/>',
    "rocket": '<path d="M12 3c4 2 6 6 5.5 10.5L15 16H9l-2.5-2.5C6 9 8 5 12 3z"/><circle cx="12" cy="9.5" r="1.8"/><path d="M9 16l-2 4 3.5-1.5M15 16l2 4-3.5-1.5"/>',
    "handshake": '<path d="M2.5 11l4-4 4 2 3-2 4 1 4 3"/><path d="M6.5 13l4.5 4.5a1.4 1.4 0 0 0 2-2M11 15l2.5 2.5a1.4 1.4 0 0 0 2-2l-3-3M14 13l2 2a1.4 1.4 0 0 0 2-2l-4-4"/>',
    "refresh": '<path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/>',
    "eye": '<path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "arrow": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/>',
    "send": '<path d="M20.5 3.5L3 11l7 2.5 2.5 7z"/><path d="M10 13.5l5-5"/>',
}


def icon(name, size=22, color="#C9A04E", sw=1.5, fill="none"):
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" '
            f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'{ICONS[name]}</svg>')


# ------------------------------------------------------------------
# Logos (SVG)
# ------------------------------------------------------------------
def aivora_mark(size=40, color="#E8CD8A"):
    # A stylised "A" inside a faceted diamond, with a spark = AI
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none">
  <path d="M32 3 L61 32 L32 61 L3 32 Z" stroke="{color}" stroke-width="1.6" fill="none"/>
  <path d="M32 11 L53 32 L32 53 L11 32 Z" stroke="{color}" stroke-width="0.6" fill="none" opacity="0.55"/>
  <path d="M20 45 L32 17 L44 45" stroke="{color}" stroke-width="3" fill="none" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M25.5 36 L38.5 36" stroke="{color}" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M46 14 L47.4 18.6 L52 20 L47.4 21.4 L46 26 L44.6 21.4 L40 20 L44.6 18.6 Z" fill="{color}" stroke="none"/>
</svg>'''


def aivora_logo(size=34, color="#E8CD8A", sub="#BFB3A0"):
    return f'''<table class="alogo"><tr>
<td class="alogo-mark">{aivora_mark(size, color)}</td>
<td class="alogo-txt"><div class="alogo-name" style="color:{color}">AIVORA</div>
<div class="alogo-sub" style="color:{sub}">STUDIO</div></td></tr></table>'''


def arch_svg(w=150, h=190, color="#C9A04E"):
    # قوس مستوحى من مدخل المحل ذي الأقواس الذهبية
    return f'''<svg width="{w}mm" height="{h}mm" viewBox="0 0 150 190" fill="none" preserveAspectRatio="none">
  <path d="M4 190 V70 A71 71 0 0 1 146 70 V190" stroke="{color}" stroke-width="0.7" fill="none"/>
  <path d="M10 190 V72 A65 65 0 0 1 140 72 V190" stroke="{color}" stroke-width="0.3" fill="none" opacity="0.6"/>
</svg>'''


def footer(n, dark=False, label="منظومة الأنباري الذكية"):
    cls = "footer dark" if dark else "footer"
    return f'''<div class="{cls}"><table><tr>
<td class="f-r">{label}<span class="f-dot">◆</span>{STORE["name"]}</td>
<td class="f-l"><span class="f-brand">AIVORA STUDIO</span><span class="pn">{n:02d}</span></td>
</tr></table></div>'''


def head(num, ar, en, dark=False):
    c = " dark" if dark else ""
    return f'''<div class="head{c}"><div class="kicker"><span class="k-num">{num}</span><span class="k-en">{en}</span></div>
<h1>{ar}</h1><div class="rule"></div></div>'''


# ------------------------------------------------------------------
# CSS
# ------------------------------------------------------------------
CSS = r"""
@font-face{font-family:"SF Arabic";src:url(FONTS/SFArabic-Light.ttf);font-weight:300}
@font-face{font-family:"SF Arabic";src:url(FONTS/SFArabic-Regular.ttf);font-weight:400}
@font-face{font-family:"SF Arabic";src:url(FONTS/SFArabic-Medium.ttf);font-weight:500}
@font-face{font-family:"SF Arabic";src:url(FONTS/SFArabic-Semibold.ttf);font-weight:600}
@font-face{font-family:"SF Arabic";src:url(FONTS/SFArabic-Bold.ttf);font-weight:700}
@font-face{font-family:"SF Arabic";src:url(FONTS/SFArabic-Heavy.ttf);font-weight:800}
@font-face{font-family:"Cormorant Garamond";src:url(FONTS/cormorant-garamond-latin-300-normal.woff);font-weight:300}
@font-face{font-family:"Cormorant Garamond";src:url(FONTS/cormorant-garamond-latin-400-normal.woff);font-weight:400}
@font-face{font-family:"Cormorant Garamond";src:url(FONTS/cormorant-garamond-latin-500-normal.woff);font-weight:500}
@font-face{font-family:"Cormorant Garamond";src:url(FONTS/cormorant-garamond-latin-600-normal.woff);font-weight:600}
@font-face{font-family:"Cormorant Garamond";src:url(FONTS/cormorant-garamond-latin-700-normal.woff);font-weight:700}
@font-face{font-family:"Cormorant Garamond";src:url(FONTS/cormorant-garamond-latin-400-italic.woff);font-weight:400;font-style:italic}
@font-face{font-family:"Cormorant Garamond";src:url(FONTS/cormorant-garamond-latin-500-italic.woff);font-weight:500;font-style:italic}

@page{size:210mm 297mm;margin:0}
*{box-sizing:border-box}
html{direction:rtl}
body{margin:0;font-family:"SF Arabic","Cormorant Garamond";font-size:9.6pt;line-height:1.75;color:#2A251D;
  -weasy-hyphens:none;font-variant-numeric:lining-nums}
.en{font-family:"Cormorant Garamond";direction:ltr;unicode-bidi:isolate}
.ltr{direction:ltr;unicode-bidi:isolate}
p{margin:0 0 3mm}
table{border-collapse:collapse}

.page{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;background:#F7F2E9}
.page:last-child{page-break-after:auto}
.page.dark{background:#0C0B0A;color:#E9E1D2}
.inner{position:absolute;top:20mm;right:18mm;width:174mm}

/* frame lines */
.frame{position:absolute;top:8mm;right:8mm;width:194mm;height:281mm;border:0.35mm solid #C9A04E;opacity:.55}
.frame2{position:absolute;top:9.6mm;right:9.6mm;width:190.8mm;height:277.8mm;border:0.15mm solid #C9A04E;opacity:.35}

/* footer — width explicit */
.footer{position:absolute;bottom:9mm;right:18mm;width:174mm;height:8mm;border-top:0.2mm solid #D8C9AE;padding-top:2mm}
.footer table{width:174mm;table-layout:fixed}
.footer td{font-size:7.2pt;color:#8A7C66;vertical-align:middle;padding:0}
.footer .f-r{text-align:right;width:120mm}
.footer .f-l{text-align:left;width:54mm;direction:ltr}
.footer .f-dot{color:#C9A04E;font-size:5pt;padding:0 2mm;vertical-align:1px}
.footer .f-brand{font-family:"Cormorant Garamond";letter-spacing:1.6pt;font-size:7.5pt;font-weight:600;color:#9A7430;padding-right:3mm}
.footer .pn{direction:ltr;unicode-bidi:isolate;font-family:"Cormorant Garamond";font-weight:600;font-size:10pt;color:#2A251D;
  border-left:0.2mm solid #C9A04E;padding-left:3mm}
.footer.dark{border-top-color:#3A3226}
.footer.dark td{color:#8E8272}
.footer.dark .pn{color:#E8CD8A}
.footer.dark .f-brand{color:#C9A04E}

/* headings */
.head{margin-bottom:7mm}
.kicker{font-size:8pt;color:#9A7430;margin-bottom:1mm}
.k-num{font-family:"Cormorant Garamond";font-weight:600;font-size:13pt;color:#C9A04E;padding-left:3mm;direction:ltr;unicode-bidi:isolate}
.k-en{font-family:"Cormorant Garamond";font-style:italic;font-size:12pt;letter-spacing:.4pt;color:#9A7430;direction:ltr;unicode-bidi:isolate}
h1{font-weight:700;font-size:25pt;line-height:1.35;margin:0;color:#14110D}
.head.dark h1{color:#F3E7CC}
.head.dark .k-en{color:#C9A04E}
.rule{width:28mm;height:0.7mm;background:linear-gradient(90deg,#9A7430,#E8CD8A,#9A7430);margin-top:3mm}
.lead{font-size:11.2pt;line-height:1.85;color:#4A4032;font-weight:400}
.dark .lead{color:#CFC4B1}
h2{font-size:13pt;font-weight:700;margin:0 0 1.5mm;color:#14110D;line-height:1.5}
h3{font-size:10.6pt;font-weight:700;margin:0 0 1mm;color:#14110D;line-height:1.5}
.dark h2,.dark h3{color:#F0E4C8}
.muted{color:#7A6E5E}
.gold{color:#B8893A}
.dark .gold{color:#E8CD8A}

/* cards */
.card{background:#FFFFFF;border:0.25mm solid #E6DAC4;border-radius:2.5mm;padding:4.5mm 5mm}
.card.dk{background:#15130F;border-color:#2E281E}
.card p{font-size:9pt;line-height:1.75;margin:0;color:#554A3B}
.card.dk p{color:#BDB19E}
.ic{vertical-align:middle}
.icbox{width:10mm;height:10mm;border-radius:50%;background:#14110D;text-align:center;padding-top:1.9mm;margin-bottom:2.5mm}
.icbox.light{background:#F3EADA}
.impact{margin-top:2mm;font-size:8.2pt;color:#9A7430;font-weight:600}
.impact:before{content:"◆  ";font-size:6pt;vertical-align:1px}

.grid2{width:174mm;table-layout:fixed}
.grid2 td{width:50%;vertical-align:top;padding:0}
.grid3{width:174mm;table-layout:fixed}
.grid3 td{vertical-align:top;padding:0}
.gap{width:4mm !important}

/* bullets */
ul.gl{list-style:none;padding:0;margin:0}
ul.gl li{position:relative;padding-right:5.5mm;margin-bottom:2mm;font-size:9.4pt;line-height:1.75}
ul.gl li:before{content:"";position:absolute;right:0;top:2.2mm;width:1.8mm;height:1.8mm;background:#C9A04E;transform:rotate(45deg)}
ul.gl li b{color:#14110D;font-weight:700}
.dark ul.gl li b{color:#F0E4C8}

.feat{width:100%;table-layout:fixed}
.feat td{vertical-align:top;padding:0 0 4.2mm}
.feat .fi{width:13mm}
.feat .fi .icbox{margin:0}
.feat h3{margin-bottom:.6mm}
.feat p{font-size:9pt;color:#554A3B;margin:0;line-height:1.75}
.dark .feat p{color:#BDB19E}

.pill{display:inline-block;border:0.25mm solid #C9A04E;border-radius:10mm;padding:.4mm 3mm;font-size:7.8pt;color:#9A7430;margin:0 0 1.5mm 1.5mm;background:#FBF6EC}
.dark .pill{background:#17140F;color:#E8CD8A;border-color:#5C4A2A}

.quote{border-right:0.8mm solid #C9A04E;padding:1mm 5mm 1mm 0;font-size:11.5pt;line-height:1.9;color:#3A3226;font-weight:500}
.dark .quote{color:#E9DDC4}

/* numbered badges */
.num{font-family:"Cormorant Garamond";font-weight:600;font-size:22pt;line-height:1;color:#C9A04E;direction:ltr;unicode-bidi:isolate}

/* === alogo === */
.alogo{border-collapse:collapse;direction:ltr}
.alogo td{padding:0;vertical-align:middle}
.alogo-txt{padding-left:2.4mm !important;text-align:left}
.alogo-name{font-family:"Cormorant Garamond";font-weight:600;font-size:15pt;letter-spacing:4.2pt;line-height:1}
.alogo-sub{font-family:"Cormorant Garamond";font-weight:500;font-size:7pt;letter-spacing:5.6pt;line-height:1;margin-top:1.3mm}

/* ==== MOCKUPS ==== */
.phone{position:absolute;width:64mm;height:132mm;background:#050505;border-radius:10mm;padding:2.2mm;
  border:0.5mm solid #3A342A}
.screen{position:relative;width:100%;height:100%;border-radius:8mm;overflow:hidden;background:#0F0D0B}
.notch{position:absolute;top:2mm;left:22mm;width:15mm;height:4.2mm;border-radius:3mm;background:#000;z-index:5}
.sbar{position:absolute;top:2.2mm;right:5mm;width:49.5mm;height:4mm;font-size:6pt;color:#fff}
.sbar .t{position:absolute;left:1mm;top:0;font-family:"Cormorant Garamond";font-weight:700;font-size:7pt;direction:ltr}
.sbar .b{position:absolute;right:0;top:.6mm;width:5mm;height:2.4mm;border:0.25mm solid #fff;border-radius:.6mm}
.sbar .b:after{content:"";position:absolute;top:.3mm;left:.3mm;width:3mm;height:1.2mm;background:#fff}

.browser{position:absolute;background:#0F0D0B;border-radius:2.5mm;border:0.35mm solid #3A342A;overflow:hidden}
.bbar{height:7mm;background:#1B1814;position:relative;border-bottom:0.2mm solid #2E281E}
.bbar .dots{position:absolute;left:3mm;top:2.4mm;direction:ltr}
.bbar .dots span{display:inline-block;width:2mm;height:2mm;border-radius:50%;margin-right:1.2mm}
.bbar .url{position:absolute;left:30mm;right:30mm;top:1.5mm;height:4mm;border-radius:2mm;background:#0F0D0B;
  font-family:"Cormorant Garamond";font-size:7pt;color:#9E927F;text-align:center;line-height:4mm;direction:ltr}

.pcard{background:#17140F;border:0.2mm solid #2E281E;border-radius:2mm;overflow:hidden}
.pcard img{display:block;width:100%;object-fit:cover}
.pcard .pb{padding:1.6mm 2mm 2mm}
.pcard .pn2{font-size:6.6pt;font-weight:600;color:#F0E4C8;line-height:1.45}
.pcard .pm{font-size:5.6pt;color:#A39681;line-height:1.5}
.pcard .pm .ltr{font-family:"Cormorant Garamond";font-weight:600;font-size:6.6pt;color:#E8CD8A}
.wa{display:block;margin-top:1.2mm;background:linear-gradient(135deg,#B8893A,#E8CD8A);color:#14110D;border-radius:1.4mm;
  text-align:center;font-size:5.8pt;font-weight:700;padding:.5mm 0}
.chip{display:inline-block;border-radius:6mm;padding:.2mm 2.2mm;font-size:5.8pt;margin:0 0 1mm 1mm;border:0.2mm solid #3A3226;color:#CFC4B1}
.chip.on{background:#C9A04E;color:#14110D;border-color:#C9A04E;font-weight:700}
.live{display:inline-block;width:1.6mm;height:1.6mm;border-radius:50%;background:#4CC38A;margin-left:1mm;vertical-align:.2mm}

.bub{border-radius:3mm;padding:1.6mm 2.6mm;font-size:6.6pt;line-height:1.65;margin-bottom:2mm;max-width:44mm}
.bub.me{background:#C9A04E;color:#14110D;margin-right:auto;margin-left:0;border-bottom-left-radius:.6mm}
.bub.bot{background:#1F1B16;color:#EDE3CF;border:0.2mm solid #2E281E;border-bottom-right-radius:.6mm}
.bub .ltr{font-family:"Cormorant Garamond";font-weight:700}

.kpi{background:#17140F;border:0.2mm solid #2E281E;border-radius:2mm;padding:2.2mm 2.6mm}
.kpi .kl{font-size:6pt;color:#A39681}
.kpi .kv{font-family:"Cormorant Garamond";font-weight:600;font-size:15pt;color:#F3E7CC;line-height:1.1;direction:ltr;unicode-bidi:isolate}
.kpi .ku{font-size:6pt;color:#C9A04E}

.dtab{width:100%;table-layout:fixed}
.dtab th{font-size:5.8pt;color:#8E8272;font-weight:500;text-align:right;padding:1mm 1.5mm;border-bottom:0.2mm solid #2E281E}
.dtab td{font-size:6.2pt;color:#E3D8C4;padding:1.25mm 1.5mm;border-bottom:0.2mm solid #221E18}
.dtab td .ltr{font-family:"Cormorant Garamond";font-weight:600;font-size:7pt}
.st{display:inline-block;border-radius:3mm;padding:0 1.6mm;font-size:5.4pt;font-weight:600}
.st.g{background:#16301F;color:#6FD39C}
.st.y{background:#3A2F14;color:#E8CD8A}
.st.b{background:#16263A;color:#8CB8EE}
.st.r{background:#3A1A16;color:#EE9C8C}

.caption{font-size:8.4pt;color:#A39681;line-height:1.7}
.caption b{color:#E8CD8A;font-weight:600}
.mlabel{font-family:"Cormorant Garamond";font-style:italic;font-size:10pt;color:#C9A04E;direction:ltr;unicode-bidi:isolate}

.toc td{padding:1.9mm 0;border-bottom:0.2mm solid #E3D6BE;font-size:9.6pt;vertical-align:middle}
.toc .tn{font-family:"Cormorant Garamond";font-weight:600;font-size:12pt;color:#C9A04E;width:9mm;text-align:right}
.toc .tp{font-family:"Cormorant Garamond";font-weight:600;font-size:11pt;color:#8A7C66;width:8mm;text-align:left}

.ps{width:174mm;table-layout:fixed}
.ps th{background:#14110D;color:#E8CD8A;font-size:8.6pt;font-weight:600;text-align:right;padding:2.4mm 3mm}
.ps td{padding:2.2mm 3mm;font-size:8.5pt;line-height:1.6;vertical-align:top;border-bottom:0.2mm solid #E3D6BE;color:#3A3226}
.ps tr:nth-child(even) td{background:#FBF7F0}
.ps td.c1{font-weight:700;color:#14110D}
.ps td.c2{color:#9A7430;font-weight:600}
"""

# ------------------------------------------------------------------
# PAGES
# ------------------------------------------------------------------
pages = []

# ---------- 1. COVER ----------
pages.append(f'''
<section class="page dark" style="background:#0A0908">
  <div style="position:absolute;top:0;right:0;width:210mm;height:297mm;background:radial-gradient(ellipse at 50% 42%, #2A2014 0%, #0A0908 62%)"></div>
  <div class="frame"></div><div class="frame2"></div>
  <div style="position:absolute;top:20mm;right:22mm;width:166mm">
    <table style="width:166mm;table-layout:fixed"><tr>
      <td style="text-align:right;vertical-align:middle;font-size:8.4pt;color:#A39681;width:90mm">عرض تقني مقدَّم إلى<br><span style="color:#E8CD8A;font-weight:600;font-size:9.6pt">إدارة {STORE["name"]}</span></td>
      <td style="vertical-align:middle;width:76mm"><div style="float:left">{aivora_logo(30)}</div></td>
    </tr></table>
  </div>

  <div style="position:absolute;top:44mm;right:30mm;width:150mm;height:150mm">{arch_svg(150,150)}</div>
  <div style="position:absolute;top:62mm;right:67.5mm;width:75mm;height:75mm;border-radius:50%;border:0.6mm solid #C9A04E;padding:2.2mm">
    <img src="{a('p_set.jpg')}" style="width:100%;height:100%;border-radius:50%;object-fit:cover">
  </div>
  <div style="position:absolute;top:146mm;right:0;width:210mm;text-align:center">
    <div style="font-family:'Cormorant Garamond';letter-spacing:6pt;font-size:10.5pt;color:#C9A04E;direction:ltr">AL-ANBARI JEWELRY · BAGHDAD</div>
    <div style="font-size:38pt;font-weight:700;color:#E8CD8A;line-height:1.35;margin-top:1mm">{STORE["name"]}</div>
  </div>

  <div style="position:absolute;top:190mm;right:30mm;width:150mm;text-align:center">
    <div style="width:150mm;height:0.25mm;background:linear-gradient(90deg,#0A0908,#C9A04E,#0A0908)"></div>
    <div style="font-size:21pt;font-weight:700;color:#F6EEDC;margin-top:7mm;line-height:1.5">منظومة الأنباري الذكية</div>
    <div style="font-size:11pt;color:#CFC4B1;margin-top:2mm;line-height:1.8">متجر إلكتروني، مساعد ذكي، أدوات للموظف، ونظام محاسبي كامل<br>تعمل معاً على قاعدة بيانات واحدة</div>
    <div style="font-family:'Cormorant Garamond';font-style:italic;font-size:13pt;color:#C9A04E;margin-top:4mm;direction:ltr">The Smart Jewelry System — A Proposal by Aivora Studio</div>
  </div>

  <div style="position:absolute;bottom:18mm;right:22mm;width:166mm">
    <table style="width:166mm;table-layout:fixed"><tr>
      <td style="text-align:right;font-size:7.8pt;color:#8E8272;width:110mm">{icon("pin",11,"#C9A04E")} {STORE["address"]}</td>
      <td style="text-align:left;font-size:7.8pt;color:#8E8272;width:56mm">{DATE_AR}</td>
    </tr></table>
  </div>
</section>''')

# ---------- 2. INTRO + TOC ----------
toc = [
    ("01", "عن Aivora Studio", "03"),
    ("02", "التحديات الحالية لمتاجر الذهب", "04"),
    ("03", "منظومة واحدة لثلاثة مستفيدين", "06"),
    ("04", "المتجر الإلكتروني الاحترافي", "07"),
    ("05", "المساعد الذكي للزبون", "08"),
    ("06", "أداة قياس الخاتم", "09"),
    ("07", "داشبورد الموظف مع مساعد ذكي", "10"),
    ("08", "النظام المحاسبي الكامل", "11"),
    ("09", "نماذج الواجهات", "12"),
    ("10", "كيف تترابط المنظومة", "15"),
    ("11", "من المشكلة إلى الحل", "16"),
    ("12", "خطوات العمل", "17"),
    ("13", "لماذا Aivora", "18"),
    ("14", "الخطوة القادمة", "19"),
]
toc_rows = "".join(f'<tr><td class="tn">{n}</td><td>{t}</td><td class="tp">{p}</td></tr>' for n, t, p in toc)
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("—", "من محلٍّ موثوق إلى منظومة ذكية", "Introduction")}
    <table class="grid2"><tr>
      <td style="width:92mm;padding-left:8mm">
        <p class="lead" style="margin-bottom:4mm">إلى إدارة {STORE["name"]} المحترمة،</p>
        <p>بنت {STORE["name"]} اسماً موثوقاً في سوق الذهب ببغداد، ومجتمعاً رقمياً كبيراً يتابع كل تشكيلة جديدة وكل تغيّر في السعر. ومع هذا الحضور يزداد الضغط اليومي على المحل: رسائل لا تتوقف، وأسعار تتغير كل صباح، وحسابات تُدار بين الدفاتر والذاكرة.</p>
        <p>نقترح في هذا العرض <b>منظومة ذكية متكاملة، وليس مجرد موقع إلكتروني</b>. منظومة تخدم الزبون وهو يتصفح ويختار، وتخدم الموظف وهو يبيع ويحاسب، وتمنح الإدارة صورة كاملة وواضحة للمخزون والأرباح في أي لحظة.</p>
        <p>وقد كتبنا هذا العرض ونحن نضع أنفسنا في مكان صاحب المحل: ما الذي يستهلك وقته؟ أين يضيع الربح؟ وما الذي يرهق الموظف في يوم مزدحم؟ ثم بنينا كل جزء من المنظومة ليجيب عن سؤال حقيقي.</p>
        <div class="quote" style="margin-top:6mm">القاعدة التي نعمل بها: كل ميزة تُسهّل على الموظف بقدر ما تُسهّل على الزبون.</div>
        <div style="margin-top:8mm">
          <div style="display:inline-block;width:26mm;text-align:center">{icon("user",20)}<div style="font-size:8.4pt;font-weight:600;margin-top:1mm">الزبون</div></div>
          <div style="display:inline-block;width:26mm;text-align:center">{icon("users",20)}<div style="font-size:8.4pt;font-weight:600;margin-top:1mm">الموظف</div></div>
          <div style="display:inline-block;width:26mm;text-align:center">{icon("chart",20)}<div style="font-size:8.4pt;font-weight:600;margin-top:1mm">الإدارة</div></div>
        </div>
      </td>
      <td style="width:82mm">
        <div class="card" style="padding:5mm 6mm">
          <div class="mlabel" style="font-size:12pt">Contents</div>
          <div style="font-weight:700;font-size:12pt;margin-bottom:2mm">محتويات العرض</div>
          <table class="toc" style="width:70mm;table-layout:fixed">{toc_rows}</table>
        </div>
      </td>
    </tr></table>
  </div>
  {footer(2)}
</section>''')

# ---------- 3. ABOUT AIVORA ----------
TECH = "".join(f'<span class="pill">{t}</span>' for t in [
    "WhatsApp Business API", "Instagram Messaging", "نماذج ذكاء اصطناعي تفهم العربية", "قارئ الباركود وطابعة الملصقات",
    "الموازين الإلكترونية", "طابعات الفواتير", "استضافة سحابية آمنة", "نسخ احتياطي يومي", "تطبيقات ويب تعمل على أي جهاز"])
services = [
    ("globe", "تطوير المواقع والمتاجر", "مواقع ومتاجر إلكترونية سريعة وفاخرة، مصممة للعربية أولاً وللموبايل قبل كل شيء."),
    ("bot", "حلول الذكاء الاصطناعي", "مساعدات ذكية تفهم اللهجة العراقية، وتعمل على واتساب وانستغرام والموقع وداخل أنظمة العمل."),
    ("receipt", "أنظمة نقاط البيع والمحاسبة", "أنظمة بيع ومخزون ومحاسبة مصممة لطبيعة كل نشاط، لا قوالب جاهزة تُفرض عليه."),
    ("headset", "الدعم والتشغيل المحلي", "فريق عراقي يتحدث لغتكم، يتابع التشغيل، ويدرّب الموظفين، ويبقى قريباً بعد الإطلاق."),
]
svc = ""
for i, (ic, t, d) in enumerate(services):
    svc += f'<td style="width:41mm"><div class="card dk" style="height:58mm"><div class="icbox" style="background:#221D15">{icon(ic,19,"#E8CD8A")}</div><h3>{t}</h3><p>{d}</p></div></td>'
    if i < 3:
        svc += '<td class="gap"></td>'
pages.append(f'''
<section class="page dark">
  <div style="position:absolute;top:0;left:0;width:210mm;height:110mm;background:linear-gradient(180deg,#1A150E,#0C0B0A)"></div>
  <div class="inner">
    {head("01", "عن Aivora Studio", "About the Studio", True)}
    <table style="width:174mm;table-layout:fixed"><tr>
      <td style="width:112mm;vertical-align:top;padding-left:8mm">
        <p class="lead"><b style="color:#E8CD8A">Aivora Studio</b> وكالة لتطوير المواقع وحلول الذكاء الاصطناعي، مقرّها أربيل، وتعمل مع أصحاب الأعمال في مختلف مدن العراق.</p>
        <p style="color:#BDB19E">نصمّم ونبني أنظمة رقمية تعمل فعلاً داخل المحل: متاجر إلكترونية، وأنظمة نقاط بيع ومحاسبة، ومساعدات ذكية تتحدث العربية. نؤمن بأن التقنية الجيدة لا تُرى، بل يُحسّ أثرها في سرعة الخدمة، وراحة الموظف، ووضوح الأرقام أمام الإدارة.</p>
      </td>
      <td style="width:62mm;vertical-align:top">
        <div style="border:0.25mm solid #3A3226;border-radius:2.5mm;padding:6mm 5mm;text-align:center;background:#12100C">
          <table style="margin:0 auto"><tr><td>{aivora_logo(34)}</td></tr></table>
          <div style="font-family:'Cormorant Garamond';font-style:italic;font-size:11pt;color:#C9A04E;margin-top:4mm;direction:ltr">Web · AI · Systems</div>
          <div style="font-size:8pt;color:#8E8272;margin-top:1mm">{icon("pin",10,"#C9A04E")} {AIVORA["city"]}</div>
        </div>
      </td>
    </tr></table>

    <div style="margin-top:9mm;margin-bottom:4mm"><span class="mlabel">What we do</span> <span style="font-weight:700;color:#F0E4C8;font-size:11pt">&nbsp;ماذا نقدّم</span></div>
    <table style="width:174mm;table-layout:fixed"><tr>{svc}</tr></table>

    <div style="margin-top:10mm;margin-bottom:4mm"><span class="mlabel">How we work</span> <span style="font-weight:700;color:#F0E4C8;font-size:11pt">&nbsp;طريقتنا في العمل</span></div>
    <table class="grid2"><tr>
      <td style="padding-left:6mm"><ul class="gl">
        <li><b>نبدأ من المحل لا من الشاشة:</b> نفهم طريقة البيع والحساب الفعلية قبل أن نرسم أي واجهة.</li>
        <li><b>العربية أولاً:</b> كل واجهة مصممة من اليمين إلى اليسار، بلغة يفهمها الموظف والزبون.</li>
      </ul></td>
      <td><ul class="gl">
        <li><b>بساطة الاستخدام:</b> إذا احتاج الموظف دليلاً ليستخدم النظام، فالتصميم يحتاج إلى تحسين.</li>
        <li><b>ملكية كاملة للبيانات:</b> بيانات المحل وزبائنه ملك للمحل، محفوظة ومؤمَّنة.</li>
      </ul></td>
    </tr></table>
    <div style="margin-top:8mm;margin-bottom:3mm"><span class="mlabel">Integrations</span> <span style="font-weight:700;color:#F0E4C8;font-size:11pt">&nbsp;تقنيات وتكاملات نعمل بها</span></div>
    <div>{TECH}</div>
  </div>
  {footer(3, True)}
</section>''')


# ---------- 4-5. CHALLENGES ----------
def ch_card(i, ic, title, body, impact, h):
    return f'''<div class="card" style="height:{h}mm">
<table style="width:100%"><tr><td style="width:12mm;vertical-align:top"><div class="icbox">{icon(ic,18,"#E8CD8A")}</div></td>
<td style="vertical-align:top;text-align:left"><span class="num" style="font-size:17pt;color:#D9C29A">{i:02d}</span></td></tr></table>
<h3>{title}</h3><p>{body}</p><div class="impact">{impact}</div></div>'''


ch1 = [
    ("tag", "تسعير يدوي مع تغيّر سعر الغرام يومياً",
     "كل صباح يُعاد حساب أسعار القطع يدوياً بعد تغيّر السعر العالمي وسعر صرف الدولار، ثم تُنشر في الستوري وتُبلَّغ للموظفين واحداً واحداً.",
     "خطأ واحد في الحساب يعني بيعاً بأقل من القيمة أو خسارة زبون"),
    ("chat", "ضغط الأسئلة على الموظفين",
     "رسائل لا تنتهي على انستغرام وواتساب: «بيش المثقال اليوم؟ هذا الموديل متوفر؟ شكد وزنه؟ يتوصل؟». يترك الموظف الزبون الواقف أمامه ليجيب الهاتف.",
     "رسائل بلا رد تعني زبائن يذهبون إلى محل آخر"),
    ("book", "محاسبة ورقية",
     "دفتر للمبيعات، وآخر للديون، وثالث لحسابات التجار. الجرد يأخذ ساعات، والخطأ الصغير لا يُكتشف إلا بعد أسابيع إن اكتُشف.",
     "لا صورة واضحة للربح الحقيقي في نهاية الشهر"),
    ("scale", "صعوبة تتبع المخزون بالغرام والعيار",
     "مخزون الذهب لا يُعدّ بالقطع فقط، بل بالوزن والعيار. مطابقة أوزان القطع مع الدفاتر عند تسليم المناوبة أو إغلاق المحل عملية مرهقة.",
     "فرق صغير في الوزن قد يعني خسارة حقيقية"),
    ("ring", "الزبون لا يعرف مقاس خاتمه",
     "خصوصاً عند شراء المحابس والهدايا عن بُعد. النتيجة: تردد في الشراء، أو تصغير وتكبير بعد البيع يستهلك وقت الصائغ والموظف.",
     "طلبات مؤجلة وتعديلات بعد البيع"),
]
c = ch1
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("02", "التحديات الحالية لمتاجر الذهب", "The Daily Reality")}
    <p class="lead" style="margin-top:-2mm;margin-bottom:6mm">كتبنا هذه التحديات كما يعيشها صاحب محل الذهب كل يوم، لا كما تبدو من خارج المحل. بعضها يسرق الوقت، وبعضها يسرق الربح بصمت.</p>
    <table class="grid2"><tr>
      <td style="padding-left:2mm">{ch_card(1,*c[0],58)}</td><td style="padding-right:2mm">{ch_card(2,*c[1],58)}</td></tr>
      <tr><td style="padding:4mm 0 0 2mm">{ch_card(3,*c[2],58)}</td><td style="padding:4mm 2mm 0 0">{ch_card(4,*c[3],58)}</td></tr>
      <tr><td style="padding:4mm 0 0 2mm">{ch_card(5,*c[4],58)}</td><td style="padding:4mm 2mm 0 0">
        <div style="height:58mm;background:#14110D;border-radius:2.5mm;padding:6mm 6mm;color:#E9DDC4">
          <div class="mlabel">Through the merchant's eyes</div>
          <div style="color:#E8CD8A;font-weight:700;font-size:11pt;margin-bottom:2mm">بعيون التاجر</div>
          <div style="font-size:10.4pt;line-height:1.9">«أريد أن أفتح المحل صباحاً وأسعاري جاهزة، وأغلقه مساءً وأنا أعرف بالضبط ماذا بعت، وماذا بقي، وكم ربحت.»</div>
        </div></td></tr>
    </table>
  </div>
  {footer(4)}
</section>''')

ch2 = [
    ("flame", "ذهب الكسر والاستبدال",
     "حساب الكسر يعتمد على الوزن والعيار ونسبة الخصم، ويُحسب غالباً بالآلة الحاسبة أمام الزبون، بلا سجل واضح لما دخل وما أُرسل للصهر أو للتاجر.",
     "خلافات مع الزبون، وكسر لا يُعرف مصيره"),
    ("handshake", "حسابات التجار والموردين بالذهب",
     "التعامل مع تجار الجملة يكون بالغرامات الصافية والمصنعيات وليس بالنقد فقط، ومتابعة رصيد كل تاجر يدوياً تفتح باب الأخطاء والخلافات.",
     "أرصدة غير دقيقة مع الموردين"),
    ("exchange", "تقلّب سعر الصرف والعملتين",
     "الشراء غالباً بالدولار والبيع بالدينار، وسعر الصرف يتغير. بدون نظام يربط الاثنين يصعب معرفة الربح الحقيقي لكل قطعة.",
     "أرباح على الورق تختلف عن الواقع"),
    ("calendar", "الحجوزات والديون والدفعات",
     "زبون يحجز قطعة بعربون، وآخر يسدد على دفعات، وثالث ينتظر قطعة تُصنع له. تتبّع ذلك بالذاكرة يُربك الموظفين ويُحرج المحل.",
     "مواعيد تُنسى وقطع محجوزة تُباع بالخطأ"),
    ("lock", "الصلاحيات والرقابة",
     "من أعطى الخصم؟ من عدّل السعر؟ من استلم الكسر؟ بدون صلاحيات وسجل لكل عملية تصعب المحاسبة ويضعف الاطمئنان داخل الفريق.",
     "لا أثر واضح لكل عملية"),
    ("bell", "فرص بيع ضائعة",
     "زبون سأل عن قطعة غير متوفرة، أو كان ينتظر انخفاض السعر، ولا أحد يعود إليه. لا توجد قاعدة بيانات للزبائن ومناسباتهم واهتماماتهم.",
     "مبيعات كانت ممكنة ولم تحدث"),
]
c = ch2
pages.append(f'''
<section class="page">
  <div class="inner">
    <div class="head"><div class="kicker"><span class="k-num">02</span><span class="k-en">Beyond the obvious</span></div>
    <h2 style="font-size:19pt">ومن واقع السوق: تحديات لا تُرى من الخارج</h2><div class="rule"></div></div>
    <p class="lead" style="margin-top:-2mm;margin-bottom:6mm">بعد دراسة طريقة عمل محلات الذهب في بغداد، وجدنا أن المشكلة لا تقف عند البيع، بل تمتد إلى الكسر والموردين والعملة والحجوزات والرقابة الداخلية.</p>
    <table class="grid2"><tr>
      <td style="padding-left:2mm">{ch_card(6,*c[0],56)}</td><td style="padding-right:2mm">{ch_card(7,*c[1],56)}</td></tr>
      <tr><td style="padding:4mm 0 0 2mm">{ch_card(8,*c[2],56)}</td><td style="padding:4mm 2mm 0 0">{ch_card(9,*c[3],56)}</td></tr>
      <tr><td style="padding:4mm 0 0 2mm">{ch_card(10,*c[4],56)}</td><td style="padding:4mm 2mm 0 0">{ch_card(11,*c[5],56)}</td></tr>
    </table>
  </div>
  {footer(5)}
</section>''')

# ---------- 6. VISION ----------
def pillar(ic, who, en, items):
    li = "".join(f"<li>{x}</li>" for x in items)
    return f'''<div class="card dk" style="height:86mm;padding:6mm 5mm">
<div class="icbox" style="background:#221D15;width:12mm;height:12mm;padding-top:2.4mm">{icon(ic,21,"#E8CD8A")}</div>
<div class="mlabel">{en}</div><h2 style="margin-bottom:3mm">{who}</h2><ul class="gl">{li}</ul></div>'''


comps = [("01", "المتجر الإلكتروني"), ("02", "المساعد الذكي"), ("03", "قياس الخاتم"), ("04", "داشبورد الموظف"), ("05", "النظام المحاسبي")]
comp_html = "".join(
    f'<td style="text-align:center;border:0.25mm solid #3A3226;background:#12100C;padding:3.5mm 1mm"><div class="num" style="font-size:16pt">{n}</div><div style="font-size:8.6pt;font-weight:600;color:#F0E4C8;margin-top:1mm">{t}</div></td>'
    + ('<td style="width:2.5mm"></td>' if i < 4 else '')
    for i, (n, t) in enumerate(comps))
pages.append(f'''
<section class="page dark">
  <div class="inner">
    {head("03", "منظومة واحدة… لثلاثة مستفيدين", "One System, Three Beneficiaries", True)}
    <p class="lead" style="margin-top:-2mm">الموقع الإلكتروني وحده يحل نصف المشكلة: يعرض القطع للزبون، لكنه يترك الموظف والإدارة كما هما. ما نقترحه هو <b style="color:#E8CD8A">منظومة تشغيل كاملة للمحل</b>، تبدأ من لحظة سؤال الزبون وتنتهي في تقرير الإدارة آخر الشهر.</p>
    <table class="grid3" style="margin-top:6mm"><tr>
      <td style="width:55.3mm">{pillar("user","الزبون","For the customer",["يرى القطع وأسعارها المحدّثة لحظياً","يسأل في أي وقت ويحصل على جواب فوري","يعرف مقاس خاتمه من موبايله","يحجز ويطلب بضغطة عبر واتساب"])}</td>
      <td class="gap"></td>
      <td style="width:55.3mm">{pillar("users","الموظف","For the staff",["لا يحسب الأسعار يدوياً بعد اليوم","لا يكرر الجواب نفسه مئة مرة","يسأل النظام بالعربي فيجيبه","يصدر الفاتورة ويحسب الكسر في ثوانٍ"])}</td>
      <td class="gap"></td>
      <td style="width:55.3mm">{pillar("chart","الإدارة","For the management",["ترى المخزون بالغرام والعيار لحظياً","تعرف الربح الحقيقي لا التقديري","تتابع أداء كل موظف وكل عملية","تستلم تقارير يومية وشهرية جاهزة"])}</td>
    </tr></table>

    <div style="margin-top:9mm;margin-bottom:3mm"><span class="mlabel">Five components</span><span style="font-weight:700;color:#F0E4C8;font-size:11pt">&nbsp; خمسة مكوّنات، قاعدة بيانات واحدة</span></div>
    <table style="width:174mm;table-layout:fixed;border-collapse:separate"><tr>{comp_html}</tr></table>
    <div style="margin-top:3mm;height:9mm;border:0.25mm solid #C9A04E;border-radius:1.5mm;background:linear-gradient(90deg,#1A150E,#2A2014,#1A150E);text-align:center;line-height:9mm;font-size:9pt;color:#E8CD8A;font-weight:600">
      {icon("db",14,"#E8CD8A")}&nbsp; قاعدة بيانات موحّدة: القطعة التي تُباع في المحل تختفي من الموقع في اللحظة نفسها
    </div>

    <div class="quote" style="margin-top:9mm">نقيس نجاح المنظومة بسؤالين: هل صار شراء الزبون أسهل؟ وهل صار يوم الموظف أخف؟ يجب أن يكون الجواب «نعم» في الحالتين.</div>
  </div>
  {footer(6, True)}
</section>''')


def feat_rows(items, dark=False, iconbg=None):
    rows = ""
    bg = iconbg or ("#221D15" if dark else "#14110D")
    for ic, t, d in items:
        rows += f'''<tr><td class="fi"><div class="icbox" style="background:{bg}">{icon(ic,18,"#E8CD8A")}</div></td>
<td><h3>{t}</h3><p>{d}</p></td></tr>'''
    return f'<table class="feat">{rows}</table>'


# ---------- 7. ONLINE STORE ----------
store_feats = [
    ("layers", "كتالوج مصنَّف وسهل التصفح", "أقسام واضحة: قلائد، أساور، خواتم ومحابس، أطقم، التشكيلة الإيطالية، ليرات وسبائك. مع فلترة حسب العيار والوزن والمناسبة."),
    ("tag", "تسعير تلقائي حسب سعر اليوم", "يُدخَل سعر الغرام لكل عيار مرة واحدة صباحاً (أو يُربط بمصدر السعر)، فتتحدّث أسعار كل القطع فوراً وفق الوزن والمصنعية، في الموقع وفي نظام البيع معاً."),
    ("gem", "صفحة خاصة لكل قطعة", "صور وفيديو عالي الدقة، الوزن الدقيق، العيار، رقم القطعة، حالتها (متوفرة، محجوزة)، ومقترحات لقطع مشابهة أو مكمّلة للطقم."),
    ("whatsapp", "طلب وحجز عبر واتساب", "زر واحد يرسل للموظف رسالة جاهزة فيها صورة القطعة ورقمها ووزنها، مع إمكانية الحجز بعربون وخيار التوصيل الذي يقدّمه المحل حالياً."),
    ("bell", "تنبيه عند انخفاض السعر", "يشترك الزبون ليصله إشعار عند انخفاض سعر الذهب، فيتحوّل منشور «انخفاض في سعر الذهب» إلى رسالة شخصية لكل زبون مهتم."),
    ("shield", "فاتورة رقمية موثَّقة", "فاتورة إلكترونية برمز QR تُثبت العيار والوزن وتاريخ الشراء، تُرسل للزبون على واتساب وتعزّز الثقة بالشراء عن بُعد."),
]


def formula_box(label, en, dark=False):
    return f'<td style="text-align:center;vertical-align:middle"><div style="border:0.3mm solid #C9A04E;border-radius:2mm;background:#FFFFFF;padding:2.5mm 1mm"><div style="font-weight:700;font-size:9pt;color:#14110D">{label}</div><div class="en" style="font-size:8.5pt;color:#9A7430;font-style:italic">{en}</div></div></td>'


op = lambda s: f'<td style="width:7mm;text-align:center;font-family:\'Cormorant Garamond\';font-size:18pt;color:#C9A04E;font-weight:600">{s}</td>'
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("04", "المتجر الإلكتروني الاحترافي", "The Online Boutique")}
    <p class="lead" style="margin-top:-2mm;margin-bottom:5mm">واجهة فاخرة تنقل أجواء صالة العرض إلى موبايل الزبون، وتُجيب عن سؤاله الأول قبل أن يطرحه: «بيش هذي القطعة اليوم؟».</p>
    <div style="background:#14110D;border-radius:2.5mm;padding:5mm 6mm;margin-bottom:6mm">
      <div style="color:#E8CD8A;font-weight:700;font-size:10pt;margin-bottom:3mm">{icon("refresh",14,"#E8CD8A")}&nbsp; معادلة التسعير التلقائي — تُطبَّق على كل قطعة لحظة تحديث السعر</div>
      <table style="width:162mm;table-layout:fixed"><tr>
        {formula_box("وزن القطعة","Weight")}{op("×")}{formula_box("سعر غرام العيار اليوم","Daily gram rate")}{op("+")}{formula_box("المصنعية","Making charge")}{op("=")}
        <td style="text-align:center;vertical-align:middle"><div style="border-radius:2mm;background:linear-gradient(135deg,#9A7430,#E8CD8A,#B8893A);padding:2.5mm 1mm"><div style="font-weight:800;font-size:9.4pt;color:#14110D">السعر النهائي</div><div class="en" style="font-size:8.5pt;color:#2A2014;font-style:italic">Live price</div></div></td>
      </tr></table>
      <div style="color:#A39681;font-size:8pt;margin-top:3mm">المصنعية مرنة: مبلغ ثابت للقطعة، أو قيمة لكل غرام، أو نسبة — حسب طريقة المحل مع كل صنف ومورد.</div>
    </div>
    <table class="grid2"><tr>
      <td style="padding-left:5mm">{feat_rows(store_feats[:3])}</td>
      <td style="padding-right:1mm">{feat_rows(store_feats[3:])}</td>
    </tr></table>
    <table style="width:174mm;table-layout:fixed;margin-top:1mm"><tr>
      <td style="width:40.5mm"><img src="{a('p_necklace.jpg')}" style="width:40.5mm;height:38mm;object-fit:cover;border-radius:2mm"></td><td class="gap"></td>
      <td style="width:40.5mm"><img src="{a('p_collection2.jpg')}" style="width:40.5mm;height:38mm;object-fit:cover;border-radius:2mm"></td><td class="gap"></td>
      <td style="width:40.5mm"><img src="{a('p_bangle.jpg')}" style="width:40.5mm;height:38mm;object-fit:cover;border-radius:2mm"></td><td class="gap"></td>
      <td style="width:40.5mm"><img src="{a('p_rings.jpg')}" style="width:40.5mm;height:38mm;object-fit:cover;border-radius:2mm"></td>
    </tr></table>
  </div>
  {footer(7)}
</section>''')

# ---------- 8. AI CUSTOMER ASSISTANT ----------
ai_feats = [
    ("clock", "يجيب على مدار 24 ساعة", "على انستغرام وواتساب والموقع، في منتصف الليل وفي أيام العطل، وبنفس جودة الرد في كل مرة."),
    ("chat", "يفهم لهجة الزبون العراقي", "«بيش المثقال؟ عدكم محابس ناعمة؟ يتوصل للكرادة؟» يفهم السؤال كما يُكتب فعلاً، ويرد بلغة مهذبة وواضحة."),
    ("db", "إجابات من بيانات المحل الحقيقية", "الأسعار والأوزان والعيارات والتوفر تُقرأ مباشرة من قاعدة البيانات، فلا يخترع معلومة ولا يعد بقطعة غير موجودة."),
    ("target", "يقترح حسب الميزانية والمناسبة", "خطوبة، زواج، مولود، تخرّج، أو هدية: يسأل عن الميزانية والذوق ثم يقترح قطعاً متوفرة فعلاً مع صورها."),
    ("headset", "يحوّل للموظف في الوقت المناسب", "عند طلب خصم، أو تصنيع خاص، أو شراء كبير، أو إذا طلب الزبون ذلك: يحوّل المحادثة مع ملخص جاهز حتى لا يعيد الزبون كلامه."),
    ("users", "يبني قاعدة بيانات للزبائن", "يحفظ اهتمامات الزبون ومناسباته (بموافقته)، ليصله عرض مناسب أو تنبيه بانخفاض السعر في الوقت المناسب."),
]
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("05", "المساعد الذكي للزبون", "The AI Concierge")}
    <table style="width:174mm;table-layout:fixed"><tr>
      <td style="width:104mm;vertical-align:top;padding-left:8mm">
        <p class="lead" style="margin-top:-2mm;margin-bottom:5mm">موظف استقبال رقمي لا يتعب ولا يغيب، يتولى الأسئلة المتكررة كلها، ويترك لفريق المحل ما يحتاج فعلاً إلى لمسة بشرية.</p>
        {feat_rows(ai_feats)}
      </td>
      <td style="width:70mm;vertical-align:top">
        <div style="background:#0F0D0B;border-radius:4mm;padding:5mm 4mm;border:0.3mm solid #2E281E">
          <table style="width:100%;margin-bottom:3mm"><tr><td style="width:9mm"><img src="{a('p_set.jpg')}" style="width:8mm;height:8mm;border-radius:50%;object-fit:cover;border:0.3mm solid #C9A04E"></td>
          <td style="padding-right:2mm"><div style="font-size:7.6pt;font-weight:700;color:#F0E4C8">مساعد الأنباري</div><div style="font-size:6pt;color:#6FD39C"><span class="live"></span>متصل الآن</div></td></tr></table>
          <div style="text-align:left"><div class="bub me" style="display:inline-block;text-align:right;max-width:52mm;font-size:7pt">مرحبا، عندي خطوبة الشهر الجاي وأريد محبس ناعم عيار 18</div></div>
          <div style="text-align:right"><div class="bub bot" style="display:inline-block;max-width:56mm;font-size:7pt">أهلاً وسهلاً، ألف مبروك مقدماً 🤍 لدينا محابس ناعمة عيار 18 متوفرة الآن. ما الميزانية التقريبية؟ وهل تعرف مقاس الخاتم؟</div></div>
          <div style="text-align:left"><div class="bub me" style="display:inline-block;text-align:right;max-width:52mm;font-size:7pt">ما أعرف المقاس</div></div>
          <div style="text-align:right"><div class="bub bot" style="display:inline-block;max-width:56mm;font-size:7pt">لا مشكلة، يمكنك قياسه من موبايلك خلال دقيقة عبر أداة القياس ↓ وبعدها أرسل لك الموديلات المناسبة لمقاسك.</div></div>
          <div style="border:0.25mm dashed #C9A04E;border-radius:2mm;padding:1.6mm;text-align:center;font-size:6.8pt;color:#E8CD8A;margin-top:1mm">{icon("ring",11,"#E8CD8A")} قِس مقاس خاتمك الآن</div>
          <div style="text-align:left"><div class="bub me" style="display:inline-block;text-align:right;max-width:52mm;font-size:7pt;margin-top:2mm">ممكن أحجي ويا موظف؟</div></div>
          <div style="text-align:right"><div class="bub bot" style="display:inline-block;max-width:56mm;font-size:7pt;margin-bottom:0">بالتأكيد، حوّلتك إلى محمد مع ملخص طلبك، سيرد عليك خلال دقائق.</div></div>
        </div>
        <div class="caption" style="color:#7A6E5E;margin-top:2.5mm;text-align:center">مثال على محادثة حقيقية تنتهي بتحويل ذكي للموظف</div>
      </td>
    </tr></table>
    <div class="quote" style="margin-top:8mm">المساعد لا يحل محل الموظف، بل يرفع عنه الأسئلة المتكررة ليتفرغ للزبون الواقف أمامه وللبيع الذي يحتاج خبرته.</div>
  </div>
  {footer(8)}
</section>''')

# ---------- 9. RING SIZER ----------
ring_steps = [
    ("01", "معايرة الشاشة", "يضع الزبون أي بطاقة بالحجم القياسي (بطاقة مصرفية أو هوية) على الشاشة ويطابق حوافها، فتعرف الأداة الحجم الحقيقي لكل مليمتر على شاشته."),
    ("02", "خاتم على الشاشة", "يضع خاتماً يناسب إصبعه على الدائرة، ويحرّك المؤشر حتى تطابق الدائرة الحافة الداخلية للخاتم تماماً."),
    ("03", "أو شريط حول الإصبع", "إن لم يكن لديه خاتم: يلف شريطاً ورقياً حول الإصبع، ويضعه على مسطرة معايَرة تظهر على الشاشة."),
    ("04", "النتيجة تُحفظ مع الطلب", "يظهر المقاس بالنظام المعتمد في المحل وبالمقاسات العالمية، ويُحفظ في ملف الزبون ويصل للموظف مع الطلب."),
]
rs = ""
for n, t, d in ring_steps:
    rs += f'''<tr><td style="width:14mm;vertical-align:top;padding-bottom:5mm;text-align:right"><div class="num" style="font-size:20pt">{n}</div></td>
<td style="vertical-align:top;padding-bottom:5mm"><h3>{t}</h3><p style="font-size:9pt;color:#554A3B;margin:0">{d}</p></td></tr>'''
ring_svg = '''<svg width="62mm" height="92mm" viewBox="0 0 62 92" fill="none">
  <rect x="3" y="2" width="56" height="88" rx="8" stroke="#C9A04E" stroke-width="0.6" fill="#14110D"/>
  <rect x="8" y="12" width="46" height="29" rx="2.5" stroke="#E8CD8A" stroke-width="0.4" stroke-dasharray="1.2 1" fill="none"/>
  <rect x="11" y="15" width="40" height="23" rx="2" fill="#2A241B" stroke="none"/>
  <rect x="15" y="24" width="7" height="5" rx="1" fill="#C9A04E" stroke="none"/>
  <circle cx="31" cy="60" r="11.5" stroke="#E8CD8A" stroke-width="3.2" fill="none"/>
  <circle cx="31" cy="60" r="9.9" stroke="#FFFFFF" stroke-width="0.35" stroke-dasharray="1 0.8" fill="none"/>
  <path d="M14 82 H48" stroke="#5C4A2A" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M14 82 H36" stroke="#E8CD8A" stroke-width="1.2" stroke-linecap="round"/>
  <circle cx="36" cy="82" r="2.2" fill="#E8CD8A" stroke="#14110D" stroke-width="0.5"/>
</svg>'''
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("06", "أداة قياس الخاتم", "The Ring Sizer")}
    <p class="lead" style="margin-top:-2mm;margin-bottom:6mm">أداة بسيطة داخل المتجر تحل مشكلة قديمة: يعرف الزبون مقاس إصبعه من موبايله في أقل من دقيقة، بدقة تكفي ليشتري بثقة، دون تطبيق إضافي أو أدوات خاصة.</p>
    <table style="width:174mm;table-layout:fixed"><tr>
      <td style="width:104mm;vertical-align:top;padding-left:8mm"><table style="width:96mm">{rs}</table></td>
      <td style="width:70mm;vertical-align:top;text-align:center">
        <div style="background:#EFE5D3;border-radius:3mm;padding:6mm 0 4mm">{ring_svg}
          <div style="font-size:7.6pt;color:#7A6E5E;margin-top:2mm">معايرة بالبطاقة، ثم مطابقة الخاتم</div></div>
      </td>
    </tr></table>
    <div style="margin-top:4mm;margin-bottom:3mm"><span class="mlabel">Why it matters</span><span style="font-weight:700;font-size:11pt">&nbsp; ماذا يكسب المحل؟</span></div>
    <table class="grid3"><tr>
      <td style="width:55.3mm"><div class="card" style="height:30mm"><h3>{icon("check",14)} أقل تعديل بعد البيع</h3><p>تصغير وتكبير أقل، ووقت أكثر للصائغ والموظف.</p></div></td><td class="gap"></td>
      <td style="width:55.3mm"><div class="card" style="height:30mm"><h3>{icon("check",14)} ثقة بشراء الهدايا</h3><p>المحابس وخواتم الخطوبة تُشترى أونلاين دون تردد.</p></div></td><td class="gap"></td>
      <td style="width:55.3mm"><div class="card" style="height:30mm"><h3>{icon("check",14)} المقاس يصل مع الطلب</h3><p>يجهّز الموظف القطعة بالمقاس الصحيح قبل وصول الزبون.</p></div></td>
    </tr></table>
    <div style="margin-top:5mm;background:#FBF6EC;border:0.25mm solid #E6DAC4;border-radius:2mm;padding:3mm 5mm;font-size:8.6pt;color:#554A3B">
      <b class="gold">نصيحة تظهر للزبون داخل الأداة:</b> القياس في المساء أدق، لأن حجم الإصبع يتغير قليلاً خلال اليوم ومع الحرارة.
    </div>
  </div>
  {footer(9)}
</section>''')

# ---------- 10. STAFF DASHBOARD ----------
qs = [
    "كم غرام أساور عيار 21 موجود عدنا هسه؟",
    "شكد صار سعر القطعة AN-2417 اليوم؟",
    "سوّي فاتورة لأم علي: محبس عيار 18، واستلمنا منها كسر عيار 21",
    "وين وصل طلب التوصيل مال زيونة؟",
    "شكد قطعة بعنا اليوم؟ وشكد وزنها؟",
    "منو الزبائن اللي عليهم دفعات هذا الأسبوع؟",
]
qhtml = "".join(f'<div style="background:#1F1B16;border:0.2mm solid #2E281E;border-radius:2.5mm;padding:2mm 3mm;margin-bottom:2mm;font-size:8.4pt;color:#EDE3CF">{icon("mic",11,"#C9A04E")}&nbsp; «{q}»</div>' for q in qs)
staff_feats = [
    ("search", "اسأل بدل أن تبحث", "لا قوائم معقدة ولا شاشات متعددة؛ يكتب الموظف أو يتكلم بالعربي، فيجيبه المساعد من بيانات المحل مباشرة."),
    ("receipt", "فاتورة في ثوانٍ، بلا أخطاء حساب", "قراءة ملصق القطعة بالباركود، وحساب السعر والمصنعية والكسر تلقائياً، وإرسال الفاتورة للزبون على واتساب."),
    ("scale", "ربط الميزان الإلكتروني", "إمكانية قراءة الوزن مباشرة من الميزان عند البيع أو استلام الكسر، بدل إدخاله يدوياً."),
    ("bell", "تنبيهات تسبق المشكلة", "قطعة محجوزة يجب ألا تُباع، دفعة مستحقة اليوم، صنف أوشك على النفاد، طلب توصيل متأخر."),
    ("lock", "آمن ومنضبط بالصلاحيات", "المساعد يحترم صلاحية كل موظف، وأي إجراء حساس كالخصم أو الإلغاء يحتاج تأكيداً ويُسجَّل باسم منفّذه."),
]
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("07", "داشبورد الموظف مع مساعد ذكي", "The Staff Copilot")}
    <p class="lead" style="margin-top:-2mm;margin-bottom:5mm">هنا يكمن الفرق الحقيقي: الموظف لا يحتاج أن يتعلم نظاماً معقداً أو يدوّر بين القوائم. يسأل كما يسأل زميله، فيحصل على الجواب أو يُنجز العملية مباشرة.</p>
    <table style="width:174mm;table-layout:fixed"><tr>
      <td style="width:98mm;vertical-align:top;padding-left:7mm">{feat_rows(staff_feats)}</td>
      <td style="width:76mm;vertical-align:top">
        <div style="background:#0F0D0B;border-radius:3mm;padding:5mm 4.5mm">
          <div style="color:#E8CD8A;font-weight:700;font-size:9.4pt;margin-bottom:1mm">{icon("bot",15,"#E8CD8A")}&nbsp; أسئلة يطرحها الموظف يومياً</div>
          <div style="color:#8E8272;font-size:7.4pt;margin-bottom:3mm">بلهجته، كتابةً أو صوتاً</div>
          {qhtml}
          <div style="border-top:0.2mm solid #2E281E;margin-top:3mm;padding-top:2.5mm;font-size:7.6pt;color:#A39681;line-height:1.7">كل سؤال يُجاب من قاعدة البيانات نفسها التي يستخدمها المتجر والمحاسبة، فلا توجد نسختان مختلفتان من الحقيقة.</div>
        </div>
      </td>
    </tr></table>
    <div style="margin-top:6mm;margin-bottom:3mm"><span class="mlabel">Before &amp; after</span><span style="font-weight:700;font-size:11pt">&nbsp; مثال: بيع محبس مع استلام كسر من الزبونة</span></div>
    <table class="grid2"><tr>
      <td style="padding-left:2mm"><div class="card" style="height:50mm;border-color:#E3D6BE;background:#FBF7F0">
        <h3 class="muted">اليوم — يدوياً</h3>
        <ul class="gl" style="font-size:8.8pt">
          <li>السؤال عن سعر اليوم أو البحث عنه في الرسائل</li>
          <li>حساب الوزن × السعر + المصنعية بالآلة الحاسبة</li>
          <li>وزن الكسر وحساب قيمته والخصم يدوياً</li>
          <li>كتابة الفاتورة، ثم تسجيل كل شيء في الدفتر</li>
        </ul></div></td>
      <td style="padding-right:2mm"><div class="card" style="height:50mm;background:#14110D;border-color:#14110D">
        <h3 style="color:#E8CD8A">مع المنظومة — ثلاث خطوات</h3>
        <ul class="gl" style="color:#E9DDC4">
          <li>مسح ملصق المحبس بالباركود</li>
          <li>وضع الكسر على الميزان واختيار العيار</li>
          <li>تأكيد العملية: فاتورة تصل للزبونة على واتساب، ومخزون وحسابات محدّثة تلقائياً</li>
        </ul></div></td>
    </tr></table>
  </div>
  {footer(10)}
</section>''')

# ---------- 11. ACCOUNTING ----------
acc = [
    ("receipt", "المبيعات", "فواتير نقدية وآجلة، بالدينار أو الدولار، مع ربط كل بيع بالموظف والقطعة."),
    ("box", "المشتريات", "فواتير الموردين بالوزن والعيار والمصنعية، وتحديث المخزون تلقائياً عند الاستلام."),
    ("scale", "المخزون بالغرام والعيار", "رصيد لحظي لكل عيار بالغرام وعدد القطع، مع ما يعادله من ذهب صافي، وجرد بالباركود."),
    ("flame", "ذهب الكسر والاستبدال", "حساب الكسر والخصم تلقائياً، وسجل لكل غرام دخل المحل ومصيره: بيع للتاجر أو صهر أو استبدال."),
    ("wallet", "ديون الزبائن والدفعات", "حجوزات بعربون، وأقساط بمواعيد، وتذكير تلقائي للزبون وللموظف."),
    ("handshake", "حسابات التجار والموردين", "أرصدة بالذهب الصافي وبالنقد لكل تاجر، مع كشف حساب واضح يمنع الخلاف."),
    ("exchange", "الدينار والدولار", "تسجيل سعر الصرف مع كل عملية، ليظهر الربح الحقيقي رغم تقلّب السعر."),
    ("layers", "المصاريف", "إيجار، رواتب، صيانة، إعلانات… مصنفة ومربوطة بتقارير الأرباح."),
    ("chart", "الأرباح", "ربح كل قطعة وكل صنف وكل عيار وكل موظف، بعد المصنعية والمصاريف وفروق الصرف."),
    ("calendar", "تقارير يومية وشهرية", "إغلاق يومي ومطابقة للوزن والصندوق، وتقرير شهري جاهز يصل للإدارة على الموبايل."),
    ("lock", "الصلاحيات حسب الموظف", "البائع يبيع، والمحاسب يراجع، والمدير يرى كل شيء. لكل دور ما يحتاجه فقط."),
    ("eye", "سجل كامل للعمليات", "من عدّل؟ متى؟ وماذا غيّر؟ أثر واضح لكل خصم أو إلغاء أو تعديل سعر."),
]
rows = ""
for r in range(4):
    rows += "<tr>"
    for col in range(3):
        ic, t, d = acc[r * 3 + col]
        rows += f'<td style="width:55.3mm;padding-bottom:3.5mm"><div class="card" style="height:41mm;padding:4mm 4.5mm"><table style="width:100%"><tr><td style="width:10mm"><div class="icbox" style="width:8.5mm;height:8.5mm;padding-top:1.4mm;margin:0">{icon(ic,15,"#E8CD8A")}</div></td><td><h3 style="margin:0;font-size:9.8pt">{t}</h3></td></tr></table><p style="margin-top:1.8mm;font-size:8.5pt">{d}</p></div></td>'
        if col < 2:
            rows += '<td class="gap"></td>'
    rows += "</tr>"
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("08", "النظام المحاسبي الكامل", "Gold-Native Accounting")}
    <p class="lead" style="margin-top:-2mm;margin-bottom:5mm">نظام محاسبي مصمم لمحل ذهب تحديداً: يفهم الغرام والعيار والمصنعية والكسر، لا مجرد أرقام في جدول. يستبدل الدفاتر كلها، ويمنح الإدارة صورة دقيقة في أي لحظة.</p>
    <table style="width:174mm;table-layout:fixed">{rows}</table>
  </div>
  {footer(11)}
</section>''')

# ---------- 12. MOCKUP — STORE (mobile + desktop) ----------
def sbar():
    return '<div class="notch"></div><div class="sbar"><span class="t">9:41</span><span class="b"></span></div>'


def pc(img, name, w, k, h=24, btn=True):
    b = '<span class="wa">اطلب عبر واتساب</span>' if btn else ''
    return f'''<div class="pcard"><img src="{a(img)}" style="height:{h}mm"><div class="pb">
<div class="pn2">{name}</div><div class="pm"><span class="ltr">{w} g</span> · عيار {k}</div>{b}</div></div>'''


mobile_store = f'''
<div class="phone" style="top:0;right:0">
 <div class="screen">
  {sbar()}
  <div style="position:absolute;top:9mm;right:4mm;width:51.2mm">
    <table style="width:100%"><tr>
      <td style="text-align:right"><div style="font-size:9pt;font-weight:800;color:#E8CD8A;line-height:1.2">مجوهرات الأنباري</div><div style="font-family:'Cormorant Garamond';font-size:5.6pt;letter-spacing:1.6pt;color:#9E927F;direction:ltr;text-align:right">AL-ANBARI JEWELRY</div></td>
      <td style="text-align:left;width:10mm">{icon("search",12,"#E8CD8A")}</td></tr></table>
    <div style="margin-top:2mm;background:linear-gradient(135deg,#1F1910,#2E2415);border:0.2mm solid #5C4A2A;border-radius:2mm;padding:1.6mm 2.4mm">
      <table style="width:100%"><tr><td style="font-size:6pt;color:#E8CD8A;font-weight:700"><span class="live"></span>سعر الذهب اليوم</td>
      <td style="text-align:left;font-size:5.4pt;color:#9E927F">محدَّث 9:00 ص</td></tr></table>
      <div style="font-size:5.6pt;color:#CFC4B1;margin-top:.6mm">عيار 24 ▲ &nbsp;·&nbsp; عيار 21 ▲ &nbsp;·&nbsp; عيار 18 ▲ &nbsp;<span style="color:#E8CD8A">عرض الأسعار ‹</span></div>
    </div>
    <div style="margin-top:2mm;position:relative;height:25mm;border-radius:2mm;overflow:hidden">
      <img src="{a('p_collection1.jpg')}" style="width:51.2mm;height:25mm;object-fit:cover;border-radius:2mm">
      <div style="position:absolute;bottom:0;right:0;width:51.2mm;height:12mm;background:linear-gradient(0deg,rgba(0,0,0,.85),rgba(0,0,0,0));border-radius:0 0 2mm 2mm"></div>
      <div style="position:absolute;bottom:1.6mm;right:2.4mm;color:#fff;font-size:7pt;font-weight:700">التشكيلة الإيطالية الجديدة</div>
      <div style="position:absolute;bottom:2mm;left:2.4mm;font-family:'Cormorant Garamond';font-style:italic;color:#E8CD8A;font-size:7pt">New Italy</div>
    </div>
    <div style="margin-top:2mm"><span class="chip on">الكل</span><span class="chip">قلائد</span><span class="chip">أساور</span><span class="chip">محابس</span><span class="chip">أطقم</span></div>
    <table style="width:51.2mm;table-layout:fixed;margin-top:.5mm"><tr>
      <td style="width:25mm">{pc("p_necklace.jpg","قلادة مارينا إيطالية","47.86","21",19)}</td><td style="width:1.2mm"></td>
      <td style="width:25mm">{pc("p_bangle.jpg","سوار مخرّم ناعم","13.55","21",19)}</td></tr></table>
  </div>
  <div style="position:absolute;bottom:0;right:0;width:59.6mm;height:10mm;background:#16130F;border-top:0.2mm solid #2E281E">
    <table style="width:100%;table-layout:fixed;margin-top:1.8mm"><tr>
      <td style="text-align:center">{icon("gem",11,"#E8CD8A")}</td><td style="text-align:center">{icon("layers",11,"#8E8272")}</td>
      <td style="text-align:center">{icon("ring",11,"#8E8272")}</td><td style="text-align:center">{icon("chat",11,"#8E8272")}</td></tr></table>
  </div>
 </div>
</div>'''

desktop_store = f'''
<div class="browser" style="top:0;left:0;width:106mm;height:132mm">
  <div class="bbar"><div class="dots"><span style="background:#FF5F57"></span><span style="background:#FEBC2E"></span><span style="background:#28C840"></span></div><div class="url">alanbari.gold</div></div>
  <div style="position:relative;height:125mm">
    <div style="position:absolute;top:0;right:0;width:106mm;height:10mm;border-bottom:0.2mm solid #2E281E">
      <div style="position:absolute;right:5mm;top:2mm;font-size:9pt;font-weight:800;color:#E8CD8A">مجوهرات الأنباري</div>
      <div style="position:absolute;right:40mm;top:3mm;font-size:6pt;color:#CFC4B1;word-spacing:1.6mm">القلائد  الأساور  المحابس  الأطقم  الإيطالي</div>
      <div style="position:absolute;left:5mm;top:2.8mm">{icon("search",10,"#E8CD8A")}&nbsp;{icon("whatsapp",10,"#E8CD8A")}</div>
    </div>
    <div style="position:absolute;top:10mm;right:0;width:106mm;height:5mm;background:#1F1910;font-size:5.8pt;color:#E8CD8A;text-align:center;line-height:5mm">
      <span class="live"></span>أسعار اليوم محدَّثة تلقائياً — عيار 24 · عيار 21 · عيار 18
    </div>
    <div style="position:absolute;top:15mm;right:0;width:106mm;height:40mm">
      <img src="{a('p_collection2.jpg')}" style="width:106mm;height:40mm;object-fit:cover">
      <div style="position:absolute;top:0;right:0;width:70mm;height:40mm;background:linear-gradient(270deg,rgba(10,9,8,.92),rgba(10,9,8,0))"></div>
      <div style="position:absolute;top:9mm;right:6mm;width:60mm">
        <div style="font-family:'Cormorant Garamond';font-style:italic;color:#E8CD8A;font-size:9pt;direction:ltr;text-align:right">New Italy Collection</div>
        <div style="font-size:12pt;font-weight:800;color:#FFF;line-height:1.4">فخامة إيطالية<br>بلمسة الأنباري</div>
        <div style="display:inline-block;margin-top:1.5mm;background:#C9A04E;color:#14110D;font-size:6pt;font-weight:700;border-radius:1mm;padding:.4mm 3mm">تسوّق التشكيلة</div>
      </div>
    </div>
    <div style="position:absolute;top:59mm;right:5mm;width:24mm">
      <div style="font-size:6.8pt;font-weight:700;color:#F0E4C8;margin-bottom:1.5mm">تصفية</div>
      <div style="font-size:5.8pt;color:#A39681;margin-bottom:.8mm">العيار</div>
      <div><span class="chip on">21</span><span class="chip">18</span><span class="chip">24</span></div>
      <div style="font-size:5.8pt;color:#A39681;margin:1.2mm 0 .8mm">الوزن (غرام)</div>
      <div style="height:1mm;background:#2E281E;border-radius:1mm;position:relative"><div style="position:absolute;right:3mm;width:12mm;height:1mm;background:#C9A04E"></div></div>
      <div style="font-size:5.8pt;color:#A39681;margin:3mm 0 .8mm">المناسبة</div>
      <div><span class="chip">خطوبة</span><span class="chip on">زواج</span><span class="chip">هدية</span><span class="chip">مولود</span></div>
    </div>
    <div style="position:absolute;top:59mm;left:4mm;width:71mm">
      <table style="width:71mm;table-layout:fixed"><tr>
        <td style="width:22.3mm">{pc("p_necklace.jpg","قلادة مارينا","47.86","21",20)}</td><td style="width:2mm"></td>
        <td style="width:22.3mm">{pc("p_rings.jpg","طقم شرائط ذهبية","53.45","21",20)}</td><td style="width:2mm"></td>
        <td style="width:22.3mm">{pc("p_bangle.jpg","سوار مخرّم","13.55","21",20)}</td>
      </tr></table>
    </div>
  </div>
</div>'''

def spec(label, val):
    return f'<td style="border:0.2mm solid #2E281E;border-radius:1.5mm;padding:1.4mm 2mm;background:#12100C"><div style="font-size:6pt;color:#8E8272">{label}</div><div style="font-size:8pt;font-weight:700;color:#F0E4C8">{val}</div></td>'


product_page = f'''
<div style="margin-top:4mm;background:#15120D;border:0.3mm solid #3A3226;border-radius:3mm;padding:4mm">
  <table style="width:166mm;table-layout:fixed"><tr>
    <td style="width:46mm;vertical-align:top"><img src="{a('p_necklace.jpg')}" style="width:46mm;height:40mm;object-fit:cover;border-radius:2mm"></td>
    <td style="width:5mm"></td>
    <td style="vertical-align:top">
      <table style="width:100%"><tr>
        <td><div class="mlabel" style="font-size:9pt">Product page</div><div style="font-size:11pt;font-weight:800;color:#F3E7CC;line-height:1.4">قلادة مارينا إيطالية</div>
        <div style="font-size:6.8pt;color:#8E8272">رقم القطعة <span class="ltr" style="font-family:'Cormorant Garamond';font-weight:700;color:#C9A04E;font-size:8pt">AN-2417</span> · التشكيلة الإيطالية</div></td>
        <td style="text-align:left;vertical-align:top"><span class="st g" style="font-size:6.4pt;padding:.3mm 2.4mm">متوفرة</span></td>
      </tr></table>
      <table style="width:100%;table-layout:fixed;margin-top:2.2mm;border-collapse:separate;border-spacing:1.5mm 0"><tr>
        {spec("الوزن", '<span class="ltr" style="font-family:Cormorant Garamond;font-size:10pt">47.86 g</span>')}{spec("العيار", "21")}{spec("المصنعية", "حسب الموديل")}{spec("المقاس", "طول قابل للتعديل")}
      </tr></table>
      <div style="margin-top:2.4mm;font-size:7.2pt;color:#CFC4B1"><span class="live"></span>السعر النهائي يُحسب لحظياً: الوزن × سعر غرام عيار 21 اليوم + المصنعية</div>
      <div style="margin-top:2.2mm">
        <span style="display:inline-block;background:linear-gradient(135deg,#B8893A,#E8CD8A);color:#14110D;border-radius:1.5mm;font-size:7pt;font-weight:800;padding:1mm 4mm;margin-left:1.5mm">{icon("whatsapp",9,"#14110D",1.8)} اطلب عبر واتساب</span>
        <span style="display:inline-block;border:0.25mm solid #C9A04E;color:#E8CD8A;border-radius:1.5mm;font-size:7pt;font-weight:700;padding:1mm 4mm;margin-left:1.5mm">احجز بعربون</span>
        <span style="display:inline-block;border:0.25mm solid #3A3226;color:#CFC4B1;border-radius:1.5mm;font-size:7pt;padding:1mm 4mm">{icon("bell",9,"#C9A04E")} نبّهني عند انخفاض السعر</span>
      </div>
    </td>
  </tr></table>
</div>'''

pages.append(f'''
<section class="page dark">
  <div class="inner">
    {head("09", "نماذج الواجهات: المتجر", "Storefront — Mobile & Desktop", True)}
    <p class="lead" style="margin-top:-2mm">هوية مستوحاة من صالة عرض الأنباري: خزائن سوداء، وإطارات ذهبية، ومخمل دافئ.</p>
    <div style="position:relative;width:174mm;height:133mm;margin-top:5mm">
      {mobile_store}
      <div style="position:absolute;top:0;left:0;width:106mm;height:134mm">{desktop_store}</div>
    </div>
    <table style="width:174mm;table-layout:fixed;margin-top:3mm"><tr>
      <td style="width:64mm;vertical-align:top;padding-left:5mm"><div class="caption"><span class="mlabel">Mobile</span>&nbsp; شريط <b>سعر الذهب المباشر</b> وطلب بضغطة</div></td>
      <td style="width:110mm;vertical-align:top;padding-right:5mm"><div class="caption"><span class="mlabel">Desktop</span>&nbsp; <b>تصفية بالعيار والوزن والمناسبة</b> وأسعار تُحسب تلقائياً</div></td>
    </tr></table>
    {product_page}
  </div>
  {footer(12, True)}
</section>''')

# ---------- 13. MOCKUP — AI assistant + ring sizer ----------
chat_phone = f'''
<div class="phone" style="top:0;right:12mm;transform:scale(1.14);transform-origin:top right">
 <div class="screen">
  {sbar()}
  <div style="position:absolute;top:8.5mm;right:0;width:59.6mm;height:11mm;border-bottom:0.2mm solid #2E281E">
    <table style="margin:1.5mm 4mm 0 0"><tr><td><img src="{a('p_set.jpg')}" style="width:7mm;height:7mm;border-radius:50%;object-fit:cover;border:0.3mm solid #C9A04E"></td>
    <td style="padding-right:1.6mm"><div style="font-size:7pt;font-weight:700;color:#F0E4C8;line-height:1.3">مساعد الأنباري</div><div style="font-size:5.4pt;color:#6FD39C;line-height:1.3"><span class="live"></span>يرد فوراً · 24 ساعة</div></td></tr></table>
  </div>
  <div style="position:absolute;top:22mm;right:3.5mm;width:52.6mm">
    <div style="text-align:left"><div class="bub me" style="display:inline-block;text-align:right;">عدكم هدايا للمولود؟ ميزانيتي متوسطة</div></div>
    <div style="text-align:right"><div class="bub bot" style="display:inline-block;">أهلاً بك 🤍 نعم، هذه اقتراحات متوفرة الآن ومناسبة لهدية مولود:</div></div>
    <table style="width:48mm;table-layout:fixed;margin-bottom:2mm"><tr>
      <td style="width:23.5mm">{pc("p_rings2.jpg","خاتم ناعم","3.10","18",13,False)}</td><td style="width:1mm"></td>
      <td style="width:23.5mm">{pc("p_bangle.jpg","سوار صغير","6.40","21",13,False)}</td></tr></table>
    <div style="text-align:left"><div class="bub me" style="display:inline-block;text-align:right;">الثاني حلو، ممكن أحجزه؟</div></div>
    <div style="text-align:right"><div class="bub bot" style="display:inline-block;">تم إرسال طلب الحجز للموظف مع صورة القطعة ورقمها <span class="ltr">AN-1082</span>. هل تفضّل الاستلام من المحل أم التوصيل؟</div></div>
  </div>
  <div style="position:absolute;bottom:3mm;right:3.5mm;width:52.6mm;height:7.5mm;border-radius:4mm;background:#1F1B16;border:0.2mm solid #2E281E">
    <div style="position:absolute;right:3mm;top:1.6mm;font-size:6pt;color:#8E8272">اكتب رسالتك…</div>
    <div style="position:absolute;left:1mm;top:.9mm;width:5.6mm;height:5.6mm;border-radius:50%;background:#C9A04E;text-align:center;padding-top:.8mm">{icon("send",9,"#14110D",1.8)}</div>
  </div>
 </div>
</div>'''

ring_phone = f'''
<div class="phone" style="top:0;left:12mm;transform:scale(1.14);transform-origin:top left">
 <div class="screen">
  {sbar()}
  <div style="position:absolute;top:10mm;right:4mm;width:51.6mm;text-align:center">
    <div style="font-size:8pt;font-weight:800;color:#F0E4C8">قياس مقاس الخاتم</div>
    <div style="font-size:5.8pt;color:#A39681">الخطوة 2 من 3 — ضع خاتمك على الدائرة</div>
    <table style="width:30mm;margin:2mm auto 0;table-layout:fixed"><tr>
      <td><div style="height:.8mm;background:#C9A04E;border-radius:1mm"></div></td><td style="width:1mm"></td>
      <td><div style="height:.8mm;background:#C9A04E;border-radius:1mm"></div></td><td style="width:1mm"></td>
      <td><div style="height:.8mm;background:#3A3226;border-radius:1mm"></div></td></tr></table>
  </div>
  <div style="position:absolute;top:26mm;right:0;width:59.6mm;text-align:center">
    <svg width="44mm" height="44mm" viewBox="0 0 44 44" fill="none">
      <circle cx="22" cy="22" r="21" stroke="#2E281E" stroke-width="0.3" fill="none"/>
      <circle cx="22" cy="22" r="16.5" stroke="#E8CD8A" stroke-width="4" fill="none" opacity="0.9"/>
      <circle cx="22" cy="22" r="14.4" stroke="#FFFFFF" stroke-width="0.35" stroke-dasharray="1.1 0.9" fill="none"/>
      <path d="M7.6 22 H36.4" stroke="#C9A04E" stroke-width="0.3"/>
      <path d="M7.6 20.5 V23.5 M36.4 20.5 V23.5" stroke="#C9A04E" stroke-width="0.3"/>
    </svg>
  </div>
  <div style="position:absolute;top:73mm;right:4mm;width:51.6mm;text-align:center">
    <div style="font-size:5.8pt;color:#A39681">القطر الداخلي</div>
    <div style="font-family:'Cormorant Garamond';font-size:18pt;font-weight:600;color:#E8CD8A;line-height:1.1;direction:ltr">17.3 mm</div>
    <div style="margin:3mm 3mm 0;height:1.2mm;background:#2E281E;border-radius:1mm;position:relative">
      <div style="position:absolute;right:0;width:28mm;height:1.2mm;background:#C9A04E;border-radius:1mm"></div>
      <div style="position:absolute;right:26.6mm;top:-1.1mm;width:3.4mm;height:3.4mm;border-radius:50%;background:#E8CD8A;border:0.4mm solid #0F0D0B"></div>
    </div>
    <table style="width:44mm;margin:3mm auto 0;table-layout:fixed"><tr>
      <td style="text-align:center"><div style="border:0.2mm solid #3A3226;border-radius:1.5mm;padding:1mm 0"><div style="font-size:5.2pt;color:#8E8272">المقاس المحلي</div><div style="font-family:'Cormorant Garamond';font-weight:700;font-size:11pt;color:#F0E4C8">16</div></div></td>
      <td style="width:2mm"></td>
      <td style="text-align:center"><div style="border:0.2mm solid #3A3226;border-radius:1.5mm;padding:1mm 0"><div style="font-size:5.2pt;color:#8E8272">المقاس الأوروبي</div><div style="font-family:'Cormorant Garamond';font-weight:700;font-size:11pt;color:#F0E4C8">54</div></div></td>
    </tr></table>
  </div>
  <div style="position:absolute;bottom:5mm;right:4mm;width:51.6mm;height:7.5mm;border-radius:2mm;background:linear-gradient(135deg,#B8893A,#E8CD8A);text-align:center;line-height:7.5mm;font-size:6.8pt;font-weight:800;color:#14110D">احفظ المقاس وأرفقه بطلبي</div>
 </div>
</div>'''

pages.append(f'''
<section class="page dark">
  <div class="inner">
    {head("09", "نماذج الواجهات: المساعد وقياس الخاتم", "AI Concierge & Ring Sizer", True)}
    <p class="lead" style="margin-top:-2mm">تجربتان صغيرتان على شاشة الزبون، لكنهما تزيلان أكبر سببين للتردد: «ما أعرف السعر» و«ما أعرف المقاس».</p>
    <div style="position:relative;width:174mm;height:152mm;margin-top:7mm">
      {chat_phone}
      {ring_phone}
      
    </div>
    <table style="width:174mm;table-layout:fixed;margin-top:6mm"><tr>
      <td style="width:87mm;vertical-align:top;padding-left:8mm"><div class="mlabel">AI Concierge</div><div class="caption">يقترح قطعاً <b>متوفرة فعلاً</b> حسب الميزانية والمناسبة، ويحوّل طلب الحجز للموظف مع رقم القطعة وصورتها.</div></td>
      <td style="width:87mm;vertical-align:top;padding-right:8mm"><div class="mlabel">Ring Sizer</div><div class="caption">مطابقة الخاتم على شاشة معايَرة، والنتيجة <b>بالمقاس المحلي والعالمي</b> تُحفظ وتُرفق بالطلب مباشرة.</div></td>
    </tr></table>
  </div>
  {footer(13, True)}
</section>''')

# ---------- 14. MOCKUP — STAFF DASHBOARD ----------
side_items = [("chart", "الرئيسية", True), ("receipt", "فاتورة جديدة", False), ("scale", "المخزون", False), ("flame", "الكسر", False),
              ("calendar", "الحجوزات", False), ("wallet", "الديون", False), ("handshake", "التجار", False), ("layers", "التقارير", False)]
side = "".join(
    f'<div style="padding:1.6mm 2.6mm;margin-bottom:.8mm;border-radius:1.4mm;font-size:6.4pt;{"background:#2A2014;color:#E8CD8A;font-weight:700" if on else "color:#A39681"}">{icon(ic,9,"#E8CD8A" if on else "#8E8272")}&nbsp; {t}</div>'
    for ic, t, on in side_items)


def kpi(label, val, unit, trend=""):
    return f'<div class="kpi"><div class="kl">{label}</div><div class="kv">{val}</div><div class="ku">{unit}{trend}</div></div>'


dash = f'''
<div class="browser" style="top:0;right:0;width:174mm;height:146mm">
  <div class="bbar"><div class="dots"><span style="background:#FF5F57"></span><span style="background:#FEBC2E"></span><span style="background:#28C840"></span></div><div class="url">staff.alanbari.gold</div></div>
  <div style="position:absolute;top:7mm;right:0;width:32mm;height:139mm;background:#12100C;border-left:0.2mm solid #2E281E;padding:3mm 2mm">
    <div style="font-size:7.4pt;font-weight:800;color:#E8CD8A;padding:0 2.6mm 3mm">الأنباري · الموظفين</div>
    {side}
    <div style="position:absolute;bottom:4mm;right:2mm;width:28mm;border-top:0.2mm solid #2E281E;padding-top:2mm">
      <table><tr><td><div style="width:6mm;height:6mm;border-radius:50%;background:#2A2014;text-align:center;font-size:6pt;color:#E8CD8A;line-height:6mm">م</div></td>
      <td style="padding-right:1.5mm"><div style="font-size:6pt;color:#F0E4C8;line-height:1.3">محمد</div><div style="font-size:5pt;color:#8E8272;line-height:1.3">بائع · صلاحية البيع</div></td></tr></table>
    </div>
  </div>
  <div style="position:absolute;top:11mm;right:36mm;width:134mm">
    <table style="width:134mm"><tr><td><div style="font-size:9pt;font-weight:800;color:#F0E4C8">صباح الخير، محمد</div><div style="font-size:6pt;color:#8E8272">الإثنين · الأسعار محدّثة 9:00 ص <span class="live"></span></div></td>
    <td style="text-align:left;vertical-align:middle"><span class="st y">3 تنبيهات</span></td></tr></table>
    <table style="width:134mm;table-layout:fixed;margin-top:3mm"><tr>
      <td>{kpi("القطع المباعة اليوم","14","قطعة"," · ▲ عن أمس")}</td><td style="width:2.5mm"></td>
      <td>{kpi("الوزن المباع اليوم","186.4","غرام · عيار 21 و18")}</td><td style="width:2.5mm"></td>
      <td>{kpi("كسر مستلم اليوم","42.7","غرام")}</td><td style="width:2.5mm"></td>
      <td>{kpi("طلبات قيد التجهيز","6","منها 2 توصيل")}</td>
    </tr></table>

    <div style="margin-top:3.5mm;border:0.3mm solid #5C4A2A;border-radius:2.5mm;background:#15120D;padding:3mm 3.5mm">
      <table style="width:100%"><tr><td style="font-size:7pt;font-weight:700;color:#E8CD8A">{icon("bot",11,"#E8CD8A")}&nbsp; المساعد الذكي</td><td style="text-align:left;font-size:5.6pt;color:#8E8272">يجيب من بيانات المحل مباشرة</td></tr></table>
      <div style="margin-top:2mm;background:#0F0D0B;border:0.2mm solid #2E281E;border-radius:2mm;padding:1.8mm 2.5mm;font-size:6.8pt;color:#F0E4C8">{icon("mic",9,"#C9A04E")}&nbsp; كم غرام أساور عيار 21 موجود عدنا هسه؟</div>
      <table style="width:100%;margin-top:2mm;table-layout:fixed"><tr>
        <td style="width:62mm;vertical-align:top;font-size:6.6pt;color:#CFC4B1;line-height:1.7;padding-left:3mm">
          المتوفر من <b style="color:#E8CD8A">أساور عيار 21</b>: <span class="ltr" style="font-family:'Cormorant Garamond';font-weight:700;font-size:8pt;color:#F3E7CC">38</span> قطعة بوزن إجمالي <span class="ltr" style="font-family:'Cormorant Garamond';font-weight:700;font-size:8pt;color:#F3E7CC">512.8 g</span>.<br>منها 4 قطع محجوزة، وصنف «سوار مخرّم» أوشك على النفاد.
          <div style="margin-top:1.5mm"><span class="chip on">اعرض القطع</span><span class="chip">أنشئ طلب شراء</span></div>
        </td>
        <td style="width:62mm;vertical-align:top">
          <svg width="62mm" height="22mm" viewBox="0 0 62 22" fill="none">
            <path d="M0 21.5 H62" stroke="#2E281E" stroke-width="0.3"/>
            <rect x="2" y="6" width="7" height="15.5" rx="0.8" fill="#C9A04E" stroke="none"/>
            <rect x="12" y="10" width="7" height="11.5" rx="0.8" fill="#8A6C33" stroke="none"/>
            <rect x="22" y="3" width="7" height="18.5" rx="0.8" fill="#E8CD8A" stroke="none"/>
            <rect x="32" y="12" width="7" height="9.5" rx="0.8" fill="#8A6C33" stroke="none"/>
            <rect x="42" y="8" width="7" height="13.5" rx="0.8" fill="#C9A04E" stroke="none"/>
            <rect x="52" y="15" width="7" height="6.5" rx="0.8" fill="#5C4A2A" stroke="none"/>
          </svg>
          <div style="font-size:5.2pt;color:#8E8272;text-align:center">الوزن المتوفر حسب الموديل (غرام)</div>
        </td>
      </tr></table>
    </div>

    <table style="width:134mm;table-layout:fixed;margin-top:3.5mm"><tr>
      <td style="width:84mm;vertical-align:top">
        <div class="kpi" style="padding:2.2mm 2mm">
          <div style="font-size:6.8pt;font-weight:700;color:#F0E4C8;margin-bottom:1mm">آخر العمليات</div>
          <table class="dtab">
            <tr><th style="width:17mm">القطعة</th><th>الزبون</th><th style="width:14mm">الوزن</th><th style="width:15mm">الحالة</th></tr>
            <tr><td><span class="ltr">AN-2417</span></td><td>قلادة مارينا · أم علي</td><td><span class="ltr">47.86</span></td><td><span class="st g">مباعة</span></td></tr>
            <tr><td><span class="ltr">AN-1082</span></td><td>سوار صغير · حجز أونلاين</td><td><span class="ltr">6.40</span></td><td><span class="st y">محجوزة</span></td></tr>
            <tr><td><span class="ltr">AN-3305</span></td><td>طقم شرائط · توصيل زيونة</td><td><span class="ltr">53.45</span></td><td><span class="st b">بالطريق</span></td></tr>
            <tr><td><span class="ltr">KS-0091</span></td><td>كسر مستلم · استبدال</td><td><span class="ltr">6.00</span></td><td><span class="st r">للصهر</span></td></tr>
          </table>
        </div>
      </td>
      <td style="width:3mm"></td>
      <td style="width:47mm;vertical-align:top">
        <div class="kpi" style="padding:2.2mm 2.4mm">
          <div style="font-size:6.8pt;font-weight:700;color:#F0E4C8;margin-bottom:1.2mm">تنبيهات اليوم</div>
          <div style="font-size:6pt;color:#CFC4B1;line-height:1.6;margin-bottom:1.2mm">{icon("calendar",8,"#E8CD8A")} دفعة مستحقة: زبونان</div>
          <div style="font-size:6pt;color:#CFC4B1;line-height:1.6;margin-bottom:1.2mm">{icon("lock",8,"#E8CD8A")} قطعة محجوزة لا تُباع: <span class="ltr">AN-1082</span></div>
          <div style="font-size:6pt;color:#CFC4B1;line-height:1.6;margin-bottom:1.2mm">{icon("box",8,"#E8CD8A")} صنف أوشك على النفاد</div>
          <div style="font-size:6pt;color:#CFC4B1;line-height:1.6">{icon("scale",8,"#E8CD8A")} جرد نهاية اليوم: 8:30 م</div>
        </div>
      </td>
    </tr></table>
  </div>
</div>'''

pages.append(f'''
<section class="page dark">
  <div class="inner">
    {head("09", "نماذج الواجهات: داشبورد الموظف", "Staff Dashboard & Copilot", True)}
    <p class="lead" style="margin-top:-2mm">شاشة واحدة يبدأ بها الموظف يومه: الأرقام المهمة بالوزن والعدد، والتنبيهات، والمساعد الذكي الذي يجيب ويُنجز بدل البحث في القوائم.</p>
    <div style="position:relative;width:174mm;height:147mm;margin-top:6mm">{dash}</div>
    <table style="width:174mm;table-layout:fixed;margin-top:6mm"><tr>
      <td style="width:58mm;vertical-align:top;padding-left:4mm"><div class="mlabel">Ask, don't search</div><div class="caption">سؤال بالعربي أو باللهجة، <b>وجواب مع أزرار تنفيذ</b> مباشرة.</div></td>
      <td style="width:58mm;vertical-align:top;padding-left:4mm"><div class="mlabel">By weight &amp; karat</div><div class="caption">مؤشرات بالغرام والعيار، <b>لا بالقطع فقط</b>، كما يفكر تاجر الذهب.</div></td>
      <td style="width:58mm;vertical-align:top"><div class="mlabel">Role-based</div><div class="caption">كل موظف يرى ما تسمح به <b>صلاحيته</b> فقط، وكل عملية مسجلة باسمه.</div></td>
    </tr></table>
  </div>
  {footer(14, True)}
</section>''')

# ---------- 15. ARCHITECTURE ----------
# Diagram geometry (mm, relative to diagram box 174 x 150)
arch = '''<svg width="174mm" height="150mm" viewBox="0 0 174 150" fill="none" style="position:absolute;top:0;right:0">
  <circle cx="87" cy="75" r="58" stroke="#3A3226" stroke-width="0.3" stroke-dasharray="1.2 1.2" fill="none"/>
  <circle cx="87" cy="75" r="30" stroke="#5C4A2A" stroke-width="0.3" fill="none"/>
  <path d="M87 45 V22" stroke="#C9A04E" stroke-width="0.6"/>
  <path d="M87 105 V128" stroke="#C9A04E" stroke-width="0.6"/>
  <path d="M57 75 H34" stroke="#C9A04E" stroke-width="0.6"/>
  <path d="M117 75 H140" stroke="#C9A04E" stroke-width="0.6"/>
  <circle cx="87" cy="33" r="1.1" fill="#E8CD8A" stroke="none"/>
  <circle cx="87" cy="117" r="1.1" fill="#E8CD8A" stroke="none"/>
  <circle cx="45" cy="75" r="1.1" fill="#E8CD8A" stroke="none"/>
  <circle cx="129" cy="75" r="1.1" fill="#E8CD8A" stroke="none"/>
  <path d="M40 22 L62 48" stroke="#5C4A2A" stroke-width="0.35" stroke-dasharray="1 1"/>
  <path d="M134 22 L112 48" stroke="#5C4A2A" stroke-width="0.35" stroke-dasharray="1 1"/>
  <path d="M40 128 L62 102" stroke="#5C4A2A" stroke-width="0.35" stroke-dasharray="1 1"/>
  <path d="M134 128 L112 102" stroke="#5C4A2A" stroke-width="0.35" stroke-dasharray="1 1"/>
  <ellipse cx="87" cy="64" rx="15" ry="4.5" stroke="#E8CD8A" stroke-width="0.7" fill="#1F1910"/>
  <path d="M72 64 V84 A15 4.5 0 0 0 102 84 V64" stroke="#E8CD8A" stroke-width="0.7" fill="#1F1910"/>
  <path d="M72 71 A15 4.5 0 0 0 102 71 M72 78 A15 4.5 0 0 0 102 78" stroke="#C9A04E" stroke-width="0.4" fill="none"/>
  <ellipse cx="87" cy="64" rx="15" ry="4.5" stroke="#E8CD8A" stroke-width="0.7" fill="#2A2014"/>
</svg>'''


def node(top, right, ic, title, sub, w=44):
    return f'''<div style="position:absolute;top:{top}mm;right:{right}mm;width:{w}mm;background:#15120D;border:0.3mm solid #C9A04E;border-radius:2.5mm;padding:2.6mm 3mm;text-align:center">
<div>{icon(ic,16,"#E8CD8A")}</div><div style="font-size:9pt;font-weight:700;color:#F0E4C8;line-height:1.5">{title}</div><div style="font-size:6.8pt;color:#A39681;line-height:1.55">{sub}</div></div>'''


def ext(top, right, ic, title, w=34):
    return f'''<div style="position:absolute;top:{top}mm;right:{right}mm;width:{w}mm;border:0.25mm dashed #5C4A2A;border-radius:2mm;padding:1.6mm 2mm;text-align:center;background:#0C0B0A">
<span style="font-size:7pt;color:#CFC4B1">{icon(ic,10,"#C9A04E")} {title}</span></div>'''


diagram = f'''<div style="position:relative;width:174mm;height:150mm">
  {arch}
  {node(4, 65, "globe", "المتجر الإلكتروني", "كتالوج · أسعار حيّة · طلبات")}
  {node(111, 65, "receipt", "النظام المحاسبي", "مبيعات · مخزون · كسر · تقارير")}
  {node(58, 130, "bot", "المساعد الذكي", "واتساب · انستغرام · الموقع", 40)}
  {node(58, 4, "monitor", "داشبورد الموظف", "بيع · فواتير · مساعد داخلي", 40)}
  <div style="position:absolute;top:89mm;right:62mm;width:50mm;text-align:center">
    <div style="font-size:8.6pt;font-weight:800;color:#E8CD8A">قاعدة بيانات موحّدة</div>
    <div class="en" style="font-size:8pt;font-style:italic;color:#A39681">Single Source of Truth</div>
  </div>
  {ext(10, 138, "tag", "سعر الذهب اليومي")}
  {ext(10, 2, "whatsapp", "واتساب وانستغرام")}
  {ext(132, 138, "scale", "الميزان والباركود")}
  {ext(132, 2, "chart", "تقارير الإدارة")}
</div>'''
flows = [
    ("يُحدَّث سعر اليوم مرة واحدة", "فتتغير أسعار الموقع، وأجوبة المساعد، وشاشة البيع، وقيمة المخزون معاً."),
    ("تُباع قطعة في المحل", "فتختفي من الموقع فوراً، وينقص المخزون بالغرام والعيار، وتدخل في تقرير اليوم."),
    ("يحجز زبون عبر المساعد", "فيظهر الحجز للموظف، وتُقفل القطعة من البيع، ويُسجَّل العربون في الحسابات."),
]
fl = "".join(f'<td style="width:55.3mm;vertical-align:top"><div class="card dk" style="height:32mm;padding:3.5mm 4mm"><h3 style="font-size:9.4pt;color:#E8CD8A">{t}</h3><p style="font-size:8.2pt">{d}</p></div></td>' + ('<td class="gap"></td>' if i < 2 else '') for i, (t, d) in enumerate(flows))
pages.append(f'''
<section class="page dark">
  <div class="inner">
    {head("10", "كيف تترابط المنظومة", "How It All Connects", True)}
    <p class="lead" style="margin-top:-2mm;margin-bottom:4mm">كل المكوّنات تقرأ وتكتب في قاعدة بيانات واحدة. لا إدخال مكرر، ولا تعارض بين ما يراه الزبون وما يراه الموظف والإدارة.</p>
    {diagram}
    <div style="margin-top:4mm;margin-bottom:3mm"><span class="mlabel">In practice</span><span style="font-weight:700;color:#F0E4C8;font-size:11pt">&nbsp; أمثلة من يوم العمل</span></div>
    <table style="width:174mm;table-layout:fixed"><tr>{fl}</tr></table>
  </div>
  {footer(15, True)}
</section>''')

# ---------- 16. PROBLEM → SOLUTION ----------
ps = [
    ("تسعير يدوي يومي", "التسعير التلقائي", "سعر واحد صباحاً يحدّث كل القطع في كل مكان"),
    ("ضغط الأسئلة والرسائل", "المساعد الذكي للزبون", "الأسئلة المتكررة تُجاب فوراً، والموظف يتفرغ للبيع"),
    ("محاسبة ورقية", "النظام المحاسبي", "دفاتر أقل، وأرقام دقيقة يومياً وشهرياً"),
    ("المخزون بالغرام والعيار", "المخزون + الباركود + الميزان", "رصيد لحظي وجرد سريع ومطابقة عند كل مناوبة"),
    ("مقاس الخاتم مجهول", "أداة قياس الخاتم", "شراء بثقة وتعديلات أقل بعد البيع"),
    ("حساب الكسر والاستبدال", "وحدة الكسر", "حساب تلقائي وسجل واضح لكل غرام"),
    ("حسابات التجار بالذهب", "حسابات الموردين", "كشف حساب بالذهب الصافي والنقد"),
    ("تقلّب الدينار والدولار", "دعم العملتين", "ربح حقيقي رغم تغيّر الصرف"),
    ("الحجوزات والديون", "الحجوزات والأقساط", "تذكير تلقائي ولا بيع لقطعة محجوزة"),
    ("غياب الرقابة", "الصلاحيات وسجل العمليات", "كل عملية لها صاحب ووقت وسبب"),
    ("فرص بيع ضائعة", "قاعدة بيانات الزبائن والتنبيهات", "عودة الزبون عند انخفاض السعر أو توفر القطعة"),
    ("ضعف الثقة بالشراء عن بُعد", "الفاتورة الرقمية بـ QR", "إثبات العيار والوزن بيد الزبون"),
]
psr = "".join(f'<tr><td class="c1">{p}</td><td class="c2">{icon("arrow",10,"#C9A04E")}&nbsp; {s}</td><td>{r}</td></tr>' for p, s, r in ps)
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("11", "من المشكلة إلى الحل", "Problem → Solution Map")}
    <p class="lead" style="margin-top:-2mm;margin-bottom:5mm">كل تحدٍّ ذكرناه له مكوّن واضح في المنظومة يعالجه، ونتيجة ملموسة يشعر بها المحل من الأسابيع الأولى.</p>
    <table class="ps"><tr><th style="width:52mm">التحدي</th><th style="width:60mm">المكوّن في المنظومة</th><th style="width:62mm">النتيجة</th></tr>{psr}</table>
    <div style="margin-top:7mm;background:#14110D;border-radius:2.5mm;padding:5mm 6mm">
      <table style="width:162mm;table-layout:fixed"><tr>
        <td style="width:54mm;text-align:center;border-left:0.2mm solid #3A3226"><div style="color:#E8CD8A;font-weight:700;font-size:10pt">وقت أقل</div><div style="color:#A39681;font-size:8pt">على الحساب والرد والجرد</div></td>
        <td style="width:54mm;text-align:center;border-left:0.2mm solid #3A3226"><div style="color:#E8CD8A;font-weight:700;font-size:10pt">أخطاء أقل</div><div style="color:#A39681;font-size:8pt">في السعر والوزن والكسر</div></td>
        <td style="width:54mm;text-align:center"><div style="color:#E8CD8A;font-weight:700;font-size:10pt">مبيعات أكثر</div><div style="color:#A39681;font-size:8pt">من زبائن كانوا سيضيعون</div></td>
      </tr></table>
    </div>
  </div>
  {footer(16)}
</section>''')

# ---------- 17. WORK STEPS ----------
steps = [
    ("handshake", "اجتماع تعريفي", "Discovery",
     "نزور المحل ونجلس مع الإدارة والموظفين، ونتعرّف على طريقة البيع والتسعير والحسابات كما هي فعلاً.",
     ["فهم دورة العمل اليومية", "جمع النماذج والدفاتر الحالية", "تحديد الأولويات"]),
    ("target", "تحديد النطاق النهائي", "Scope",
     "نحوّل ما سمعناه إلى وثيقة واضحة: المكوّنات، والصلاحيات، والتقارير، وما يُنفَّذ أولاً.",
     ["وثيقة نطاق معتمدة", "خطة مراحل التنفيذ", "عرض سعر مخصص"]),
    ("pen", "التصميم", "Design",
     "نصمم الهوية الرقمية والواجهات بما ينسجم مع صالة عرض الأنباري، ونراجعها معكم قبل البرمجة.",
     ["واجهات الموبايل والكمبيوتر", "نماذج تفاعلية للتجربة", "اعتماد التصميم"]),
    ("code", "التطوير", "Build",
     "نبني المنظومة على مراحل، ونُدخل بيانات المخزون والتجار والزبائن، ونختبر كل مرحلة داخل المحل.",
     ["تسليم تدريجي قابل للتجربة", "إدخال البيانات الحالية", "اختبار على حالات حقيقية"]),
    ("rocket", "التسليم وتدريب الموظفين", "Launch & Training",
     "نُطلق المنظومة، وندرّب كل موظف حسب دوره، ونبقى قريبين في الأسابيع الأولى لضمان انتقال سلس.",
     ["تدريب عملي لكل دور", "دليل استخدام مختصر", "متابعة ودعم بعد الإطلاق"]),
]
st = ""
for i, (ic, t, en, d, dl) in enumerate(steps, 1):
    li = "".join(f"<li>{x}</li>" for x in dl)
    last = i == len(steps)
    line = "" if last else '<div style="position:absolute;top:14mm;right:6.6mm;width:0.3mm;height:33mm;background:#D8C9AE"></div>'
    st += f'''<div style="position:relative;height:{38 if last else 41}mm">
  {line}
  <div style="position:absolute;top:0;right:0;width:13.5mm;height:13.5mm;border-radius:50%;background:#14110D;border:0.4mm solid #C9A04E;text-align:center;padding-top:3mm">{icon(ic,18,"#E8CD8A")}</div>
  <div style="position:absolute;top:0;right:19mm;width:155mm">
    <table style="width:155mm;table-layout:fixed"><tr>
      <td style="width:88mm;vertical-align:top;padding-left:6mm"><div><span class="num" style="font-size:14pt">0{i}</span>&nbsp; <span class="mlabel">{en}</span></div><h2 style="margin-top:.5mm">{t}</h2><p style="font-size:9pt;color:#554A3B">{d}</p></td>
      <td style="width:67mm;vertical-align:top;padding-top:3mm"><div class="card" style="padding:3mm 4mm"><ul class="gl">{li}</ul></div></td>
    </tr></table>
  </div></div>'''
pages.append(f'''
<section class="page">
  <div class="inner">
    {head("12", "خطوات العمل", "How We Work Together")}
    <p class="lead" style="margin-top:-2mm;margin-bottom:6mm">مسار واضح من أول لقاء حتى يعمل الفريق على المنظومة بثقة. في كل مرحلة ترون النتيجة وتعتمدونها قبل الانتقال لما بعدها.</p>
    {st}
  </div>
  {footer(17)}
</section>''')

# ---------- 18. WHY AIVORA ----------
why = [
    ("receipt", "خبرة في أنظمة نقاط البيع", "نعرف ماذا يحدث عند الكاشير في ساعة الذروة، ونصمم لتلك اللحظة تحديداً."),
    ("globe", "خبرة في المتاجر الإلكترونية", "متاجر عربية فاخرة وسريعة، مصممة لتبيع على الموبايل لا لتُعرض فقط."),
    ("bot", "خبرة في الذكاء الاصطناعي", "مساعدات ذكية تفهم اللهجة العراقية، وتعمل على بيانات المحل الحقيقية بأمان."),
    ("headset", "دعم محلي قريب", "فريق عراقي يتحدث لغتكم، ويصل إليكم بسرعة، ولا يختفي بعد التسليم."),
    ("pen", "حلول مخصصة لا قوالب", "نبني حول طريقة عمل الأنباري، لا نطلب من المحل أن يغيّر طريقته ليناسب البرنامج."),
    ("shield", "بياناتكم ملككم", "نسخ احتياطي، وصلاحيات دقيقة، وملكية كاملة لبيانات المحل وزبائنه."),
]
wr = ""
for r in range(3):
    wr += "<tr>"
    for col in range(2):
        ic, t, d = why[r * 2 + col]
        wr += f'<td style="width:85mm;padding-bottom:4mm"><div class="card dk" style="height:31mm"><table style="width:100%"><tr><td style="width:13mm;vertical-align:top"><div class="icbox" style="background:#221D15;margin:0">{icon(ic,18,"#E8CD8A")}</div></td><td style="vertical-align:top"><h3>{t}</h3><p>{d}</p></td></tr></table></div></td>'
        if col == 0:
            wr += '<td class="gap"></td>'
    wr += "</tr>"
pages.append(f'''
<section class="page dark">
  <div class="inner">
    {head("13", "لماذا Aivora؟", "Why Aivora", True)}
    <p class="lead" style="margin-top:-2mm;margin-bottom:6mm">لأن محل الذهب يحتاج شريكاً تقنياً يفهم الغرام والعيار والمصنعية، ويفهم الزبون العراقي، ويبقى قريباً بعد الإطلاق.</p>
    <table style="width:174mm;table-layout:fixed">{wr}</table>
    <div class="quote" style="margin-top:3mm">لا نبيع برنامجاً جاهزاً؛ نبني معكم الطريقة التي سيعمل بها محلكم في السنوات القادمة.</div>
    <div style="margin-top:9mm;margin-bottom:3mm"><span class="mlabel">Our commitments</span><span style="font-weight:700;color:#F0E4C8;font-size:11pt">&nbsp; التزاماتنا معكم</span></div>
    <table style="width:174mm;table-layout:fixed;border:0.3mm solid #5C4A2A;border-radius:2.5mm;background:#12100C"><tr>
      <td style="text-align:center;padding:5mm 2mm;border-left:0.2mm solid #2E281E">{icon("eye",18,"#E8CD8A")}<div style="font-size:9pt;font-weight:700;color:#F0E4C8;margin-top:1mm">نسخة تجريبية</div><div style="font-size:7.6pt;color:#A39681">ترونها قبل الاعتماد</div></td>
      <td style="text-align:center;padding:5mm 2mm;border-left:0.2mm solid #2E281E">{icon("users",18,"#E8CD8A")}<div style="font-size:9pt;font-weight:700;color:#F0E4C8;margin-top:1mm">تدريب لكل موظف</div><div style="font-size:7.6pt;color:#A39681">حسب دوره وصلاحيته</div></td>
      <td style="text-align:center;padding:5mm 2mm;border-left:0.2mm solid #2E281E">{icon("headset",18,"#E8CD8A")}<div style="font-size:9pt;font-weight:700;color:#F0E4C8;margin-top:1mm">دعم بعد الإطلاق</div><div style="font-size:7.6pt;color:#A39681">متابعة قريبة ومباشرة</div></td>
      <td style="text-align:center;padding:5mm 2mm">{icon("refresh",18,"#E8CD8A")}<div style="font-size:9pt;font-weight:700;color:#F0E4C8;margin-top:1mm">تطوير مستمر</div><div style="font-size:7.6pt;color:#A39681">مع نمو المحل واحتياجه</div></td>
    </tr></table>
  </div>
  {footer(18, True)}
</section>''')

# ---------- 19. NEXT STEP ----------
contact = [
    ("phone", "الهاتف وواتساب", AIVORA["phone"], True),
    ("mail", "البريد الإلكتروني", AIVORA["email"], True),
    ("globe", "الموقع", AIVORA["web"], True),
    ("insta", "انستغرام", AIVORA["insta"], True),
]
cr = "".join(
    f'<tr><td style="width:12mm;padding:2.4mm 0">{icon(ic,16,"#E8CD8A")}</td><td style="font-size:8.4pt;color:#A39681;width:34mm">{lbl}</td>'
    f'<td style="text-align:left;font-family:\'Cormorant Garamond\';font-weight:600;font-size:12.5pt;color:#F3E7CC;direction:ltr">{val}</td></tr>'
    for ic, lbl, val, _ in contact)
pages.append(f'''
<section class="page dark" style="background:#0A0908">
  <div style="position:absolute;top:0;right:0;width:210mm;height:297mm;background:radial-gradient(ellipse at 50% 30%, #261D12 0%, #0A0908 60%)"></div>
  <div class="frame"></div><div class="frame2"></div>
  <div class="inner" style="top:26mm">
    <div style="text-align:center">
      <div class="mlabel" style="font-size:13pt">The Next Step</div>
      <div style="font-size:28pt;font-weight:800;color:#E8CD8A;line-height:1.4;margin-top:1mm">الخطوة القادمة</div>
      <div style="width:28mm;height:0.7mm;background:linear-gradient(90deg,#9A7430,#E8CD8A,#9A7430);margin:3mm auto 0"></div>
      <p class="lead" style="margin:6mm 14mm 0">نقترح اجتماعاً قصيراً في المحل مع الإدارة وأحد الموظفين، نناقش فيه التفاصيل ونرى طريقة العمل على أرض الواقع. بعده نقدّم لكم <b style="color:#E8CD8A">عرض سعر مخصصاً</b> مبنياً على احتياجاتكم الفعلية والمكوّنات التي تختارونها.</p>
    </div>
    <table style="width:150mm;margin:10mm auto 0;table-layout:fixed"><tr>
      <td style="width:48mm;text-align:center"><div class="num">01</div><div style="font-size:9.4pt;font-weight:700;color:#F0E4C8">حجز الاجتماع</div><div style="font-size:7.8pt;color:#A39681">في الوقت الذي يناسبكم</div></td>
      <td style="width:3mm;text-align:center;color:#5C4A2A">◆</td>
      <td style="width:48mm;text-align:center"><div class="num">02</div><div style="font-size:9.4pt;font-weight:700;color:#F0E4C8">مناقشة التفاصيل</div><div style="font-size:7.8pt;color:#A39681">المكوّنات والأولويات</div></td>
      <td style="width:3mm;text-align:center;color:#5C4A2A">◆</td>
      <td style="width:48mm;text-align:center"><div class="num">03</div><div style="font-size:9.4pt;font-weight:700;color:#F0E4C8">عرض سعر مخصص</div><div style="font-size:7.8pt;color:#A39681">حسب احتياجكم</div></td>
    </tr></table>

    <table style="width:130mm;margin:12mm auto 0"><tr><td style="border:0.3mm solid #5C4A2A;border-radius:3mm;background:#12100C;padding:6mm 8mm">
      <table style="width:114mm;margin-bottom:3mm"><tr><td>{aivora_logo(30)}</td><td style="text-align:left;font-size:8pt;color:#A39681">{AIVORA["city"]}</td></tr></table>
      <div style="height:0.2mm;background:#3A3226;margin-bottom:1mm"></div>
      <table style="width:114mm;table-layout:fixed">{cr}</table>
    </td></tr></table>

    <div style="text-align:center;margin-top:11mm">
      <div style="font-size:9pt;color:#A39681">مُعدّ خصيصاً لـ</div>
      <div style="font-size:14pt;font-weight:700;color:#E8CD8A">{STORE["name"]}</div>
      <div style="font-family:'Cormorant Garamond';font-size:10pt;color:#8E8272;direction:ltr">{STORE["insta"]}</div>
    </div>
  </div>
  {footer(19, True)}
</section>''')

# ------------------------------------------------------------------
html = f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>منظومة الأنباري الذكية — Aivora Studio</title>
<style>{CSS.replace("FONTS/", FONTS.as_uri() + "/")}</style></head>
<body>{"".join(pages)}</body></html>'''

if __name__ == "__main__":
    import sys
    OUT.mkdir(exist_ok=True)
    (OUT / "proposal.html").write_text(html, encoding="utf-8")
    pdf = OUT / "Al-Anbari-Proposal-Aivora.pdf"
    HTML(string=html, base_url=str(ROOT)).write_pdf(pdf)
    print("PDF:", pdf)
    if "--no-preview" not in sys.argv:
        import fitz
        pv = OUT / "preview"
        pv.mkdir(exist_ok=True)
        doc = fitz.open(pdf)
        for i, page in enumerate(doc, 1):
            page.get_pixmap(dpi=110).save(pv / f"page-{i:02d}.png")
        print("pages:", len(doc))
