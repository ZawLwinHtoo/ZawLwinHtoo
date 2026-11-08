"""Generate the profile's original SVGs. No packages or network calls required."""
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ASSETS = Path(__file__).resolve().parents[1] / "assets"
INK, LIME, CREAM, MUTED = "#131613", "#c9ff59", "#f4f4e8", "#a5afa0"
MONO = "Consolas, 'Liberation Mono', monospace"
SANS = "'Arial Black', 'Segoe UI', Arial, sans-serif"


def text(x, y, content, size=20, fill=CREAM, weight=400, mono=False, extra=""):
    font = MONO if mono else SANS
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{font}" '
            f'font-size="{size}" font-weight="{weight}" {extra}>{escape(content)}</text>')


def svg(name, w, h, title, content):
    art = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
{content}
</svg>
'''
    ET.fromstring(art)
    (ASSETS / name).write_text(art, encoding="utf-8")


def bug(x, y, scale=1):
    return f'''<g id="circuit-beetle" transform="translate({x} {y}) scale({scale})">
<g fill="none" stroke="{LIME}" stroke-width="5" stroke-linecap="square" stroke-linejoin="round">
<path d="M-44-20-85-44h-24m65 55h-54l-14 20m71 13-36 30v25M44-20l41-24h24M44 11h54l14 20M41 44l36 30v25"/>
<path d="M-21-85-43-113v-16M21-85l22-28v-16"/>
</g>
<g fill="{LIME}"><circle cx="-43" cy="-134" r="6"/><circle cx="43" cy="-134" r="6"/>
<path d="M-39-62a39 32 0 0 1 78 0v24h-78z"/>
<path d="M-4-29C-75-48-77 70-4 91ZM4-29C75-48 77 70 4 91Z"/>
</g>
<g fill="{INK}"><rect class="eye" x="-21" y="-68" width="10" height="10" rx="2"/><rect class="eye" x="11" y="-68" width="10" height="10" rx="2"/></g>
<path d="M-40-2h18v22h-16m78-22H22v22h16M-29 46h12m34 0h12" fill="none" stroke="{INK}" stroke-width="4"/>
</g>'''


def hero(mobile=False):
    w, h = (600, 690) if mobile else (1200, 460)
    base = f'''<defs>
<pattern id="dot-grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#8a9885" opacity=".18"/></pattern>
</defs>
<style>
.traffic{{animation:travel 9s linear infinite}}
.ring{{animation:breathe 5s ease-in-out infinite}}
.eye{{animation:blink 8s step-end infinite}}
@keyframes travel{{to{{stroke-dashoffset:-100}}}}
@keyframes breathe{{0%,100%{{opacity:.3}}50%{{opacity:.7}}}}
@keyframes blink{{0%,46%,49%,100%{{opacity:1}}47%,48%{{opacity:.1}}}}
@media(prefers-reduced-motion:reduce){{.traffic,.ring,.eye{{animation:none}}}}
</style>
<rect width="{w}" height="{h}" rx="20" fill="{INK}"/>
<rect width="{w}" height="{h}" rx="20" fill="url(#dot-grid)"/>
<g id="identity"><path d="M30 32h14v14H30zM48 32h6v6h-6zM48 42h6v12h-6z" fill="{LIME}"/>
{text(70, 48, 'ZAW LWIN HTOO', 20, weight=700, mono=True)}</g>'''
    if mobile:
        content = base + f'''
{text(30, 158, 'ENJOY', 112, weight=900, extra='letter-spacing="-6"')}
{text(30, 271, 'BUGS.', 112, LIME, 900, extra='letter-spacing="-6"')}
{text(34, 312, '@ZawLwinHtoo', 20, MUTED, mono=True)}
<circle cx="309" cy="479" r="137" fill="none" stroke="#374132"/>
<circle class="ring" cx="309" cy="479" r="116" fill="none" stroke="{LIME}" stroke-dasharray="3 12"/>
{bug(309, 485, .76)}
<path d="M30 636h540" stroke="#374132"/>
{text(30, 668, 'CODE. BREAK. LEARN. REPEAT.', 20, mono=True)}'''
    else:
        content = base + f'''
{text(904, 48, 'CURIOUS BY DEFAULT', 17, MUTED, mono=True)}
<g id="headline">
{text(44, 197, 'ENJOY', 134, weight=900, extra='letter-spacing="-7"')}
{text(44, 328, 'BUGS.', 134, LIME, 900, extra='letter-spacing="-7"')}</g>
<g id="specimen">
<circle cx="884" cy="233" r="158" fill="#1b2119" stroke="#374132"/>
<circle class="ring" cx="884" cy="233" r="139" fill="none" stroke="{LIME}" stroke-dasharray="3 14"/>
<path d="M700 233h368M884 61v344" stroke="#374132" stroke-dasharray="4 8"/>
<path d="M600 315h78v-82h48M1041 233h84v-83h45" fill="none" stroke="#46513e" stroke-width="2"/>
<path class="traffic" d="M600 315h78v-82h48" fill="none" stroke="{LIME}" stroke-width="3" pathLength="100" stroke-dasharray="8 92"/>
{bug(884, 245, .95)}
{text(1020, 352, 'BUG / 001', 15, MUTED, mono=True)}</g>
<path d="M44 391h1112" stroke="#374132"/>
{text(44, 429, 'CODE. BREAK. LEARN. REPEAT.', 20, mono=True)}
{text(964, 429, '@ZawLwinHtoo', 17, MUTED, mono=True)}'''
    svg("profile-banner-mobile.svg" if mobile else "profile-banner.svg", w, h,
        "Zaw Lwin Htoo / Enjoy bugs / Code, break, learn, repeat", content)


def route_map(x=0, y=0, scale=1):
    return f'''<g transform="translate({x} {y}) scale({scale})">
<rect width="470" height="228" rx="12" fill="#1d291e" stroke="#405437"/>
<g stroke="#354431" stroke-width="15"><path d="M0 54h470M0 174h470M64 0v228M259 0v228M405 0v228"/></g>
<g stroke="#283724" stroke-width="1"><path d="M0 54h470M0 174h470M64 0v228M259 0v228M405 0v228"/></g>
<path d="M64 174h195V54h146" fill="none" stroke="{LIME}" stroke-width="5" stroke-linejoin="round"/>
<circle cx="64" cy="174" r="13" fill="{LIME}"/><circle cx="64" cy="174" r="5" fill="{INK}"/>
<circle cx="405" cy="54" r="13" fill="{LIME}"/><circle cx="405" cy="54" r="5" fill="{INK}"/>
<rect x="238" y="109" width="42" height="35" rx="7" fill="{CREAM}" stroke="{INK}" stroke-width="3"/>
<path d="m250 131 9-10 9 10" fill="none" stroke="{INK}" stroke-width="3"/>
<rect x="94" y="145" width="105" height="28" rx="5" fill="{INK}"/>
{text(104, 164, 'DISPATCH', 14, LIME, mono=True)}
<rect x="326" y="86" width="112" height="28" rx="5" fill="{INK}"/>
{text(337, 105, 'DELIVERY', 14, LIME, mono=True)}</g>'''


def lannpya(mobile=False):
    if mobile:
        w, h = 600, 550
        content = f'''<rect width="600" height="550" rx="18" fill="#192218"/>
{text(30, 46, '01 / LOGISTICS', 18, LIME, mono=True)}
{text(30, 120, 'LannPya AI.', 64, weight=900, extra='letter-spacing="-3"')}
{text(32, 160, 'LOCAL CONTEXT. PRACTICAL TOOLS.', 17, MUTED, mono=True)}
{route_map(30, 192, 1.15)}
{text(32, 509, 'PYTHON / FASTAPI', 18, LIME, mono=True)}
{text(480, 511, '↗', 36, LIME)}'''
    else:
        w, h = 1200, 340
        content = f'''<rect width="1200" height="340" rx="18" fill="#192218"/>
{text(40, 47, '01 / LOGISTICS', 18, LIME, mono=True)}
{text(38, 143, 'LannPya AI.', 75, weight=900, extra='letter-spacing="-4"')}
{text(42, 189, 'LOCAL CONTEXT. PRACTICAL TOOLS.', 18, MUTED, mono=True)}
<rect x="40" y="248" width="238" height="42" rx="7" fill="#293724"/>
{text(56, 275, 'PYTHON / FASTAPI', 18, LIME, mono=True)}
{route_map(637, 55, 1.04)}
{text(1127, 310, '↗', 36, LIME)}'''
    svg("project-lannpya-mobile.svg" if mobile else "project-lannpya.svg", w, h,
        "LannPya AI / Delivery tooling for Myanmar", content)


def menu():
    content = f'''<rect width="580" height="360" rx="16" fill="#29201b"/>
{text(26, 42, '02 / WEB APP', 19, '#ffb184', mono=True)}
{text(24, 121, 'Menu', 63, weight=900, extra='letter-spacing="-3"')}
{text(24, 184, 'Maker.', 63, weight=900, extra='letter-spacing="-3"')}
<g transform="translate(359 96) rotate(9)">
<rect width="160" height="195" rx="9" fill="#fbdfc6"/>
<rect x="17" y="18" width="37" height="6" rx="2" fill="#a74420"/>
{text(17, 61, 'MENU', 22, '#3d261c', 900)}
<g stroke="#b47d56" stroke-width="4" stroke-linecap="round"><path d="M19 87h70m20 0h30M19 111h85m16 0h19M19 135h61m25 0h34M19 159h78m20 0h22"/></g></g>
<circle cx="488" cy="262" r="37" fill="#ff9d66"/>
<path d="M472 262h30m-11-11 11 11-11 11" fill="none" stroke="#3d261c" stroke-width="4"/>
{text(26, 323, 'CREATE / ORGANIZE', 18, '#ffb184', mono=True)}'''
    svg("project-menu.svg", 580, 360, "Menu Maker / Create and manage menus", content)


def parking():
    content = f'''<rect width="580" height="360" rx="16" fill="#172532"/>
{text(26, 42, '03 / MANAGEMENT', 19, '#89d5ff', mono=True)}
{text(24, 121, 'Parking', 63, weight=900, extra='letter-spacing="-3"')}
{text(26, 169, 'MANAGEMENT', 25, '#89d5ff', 700, mono=True)}
<g transform="translate(304 198)">
<path d="M0 0h234M0 89h234M0 0v89M78 0v89M156 0v89M234 0v89" fill="none" stroke="#3d6076" stroke-width="3"/>
<rect x="91" y="11" width="52" height="69" rx="11" fill="#89d5ff"/>
<rect x="100" y="25" width="34" height="20" rx="5" fill="#203c50"/>
<rect x="100" y="57" width="34" height="10" rx="3" fill="#203c50"/>
<path d="M20 45h37m-12-12 12 12-12 12" fill="none" stroke="#89d5ff" stroke-width="4"/>
</g>
{text(26, 324, 'USER / ADMIN', 18, '#89d5ff', mono=True)}'''
    svg("project-parking.svg", 580, 360, "Parking Management / User and admin tools", content)


def toolbox():
    items = [("python", "PY", "Python"), ("javascript", "JS", "JavaScript"),
             ("cpp", "++", "C++"), ("c", "C", "C"), ("css", "{}", "CSS")]
    for slug, glyph, label in items:
        content = f'''<rect x="1" y="1" width="190" height="66" rx="10" fill="{INK}" stroke="#3c4637"/>
<rect x="10" y="12" width="44" height="44" rx="7" fill="#293523"/>
{text(32, 40, glyph, 20, LIME, 700, True, 'text-anchor="middle"')}
{text(65, 41, label, 18, CREAM, 600)}'''
        svg(f"tool-{slug}.svg", 192, 68, label, content)


def afterword():
    content = f'''<rect width="1200" height="154" rx="16" fill="{LIME}"/>
<path d="M1065 0v154" stroke="{INK}" stroke-opacity=".2"/>
{text(34, 60, 'EVERY BUG IS', 40, INK, 900, extra='letter-spacing="-1"')}
{text(34, 110, 'A PLOT TWIST.', 40, INK, 900, extra='letter-spacing="-1"')}
{text(665, 87, 'See what I’m building next', 21, INK, 500, True)}
<path d="M1110 98l37-37m-34 0h34v34" fill="none" stroke="{INK}" stroke-width="6"/>
'''
    svg("afterword.svg", 1200, 154, "Every bug is a plot twist / See what I'm building next", content)
    mobile = f'''<rect width="600" height="236" rx="16" fill="{LIME}"/>
{text(28, 66, 'EVERY BUG IS', 44, INK, 900, extra='letter-spacing="-1"')}
{text(28, 120, 'A PLOT TWIST.', 44, INK, 900, extra='letter-spacing="-1"')}
<path d="M28 152h544" stroke="{INK}" stroke-opacity=".2"/>
{text(28, 201, 'See what I’m building next', 22, INK, 500, True)}
<path d="M521 209l30-30m-27 0h27v27" fill="none" stroke="{INK}" stroke-width="5"/>'''
    svg("afterword-mobile.svg", 600, 236, "Every bug is a plot twist / See what I'm building next", mobile)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    hero()
    hero(mobile=True)
    lannpya()
    lannpya(mobile=True)
    menu()
    parking()
    toolbox()
    afterword()
    print(f"Generated and parsed 13 SVG assets in {ASSETS}")
