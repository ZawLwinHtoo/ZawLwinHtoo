"""Project-specific editorial cards with dimensional SVG spot illustrations."""
from hashlib import sha256
from html import escape
import re
import textwrap

import generate_artwork as art

PROJECTS = {
    'lannpya-ai': ('LannPya AI', 'LOCAL INTELLIGENCE', 'Routes, addresses, possibilities.', 'routes', '#c9ff59', '#17251c'),
    'menu-maker': ('Menu Maker', 'MADE TO ORDER', 'A little taste of good design.', 'menu', '#ffb78c', '#30211d'),
    'parking-management-system': ('Parking Management', 'SPACE, SORTED', 'A place for every arrival.', 'parking', '#8ad8ff', '#172b3c'),
    'Backup-Programs': ('Backup Programs', 'THE CODE VAULT', 'Experiments worth keeping.', 'vault', '#b9a4ff', '#241e3b'),
    'colladraw': ('CollaDraw', 'CREATE TOGETHER', 'More minds. One canvas.', 'draw', '#ffb3cb', '#342030'),
    'conveyor_edge_ai': ('Conveyor Edge AI', 'INTELLIGENCE IN MOTION', 'Where the physical meets digital.', 'conveyor', '#f9d97a', '#302a1b'),
    'distributed-whiteboard': ('Distributed Whiteboard', 'IDEAS, CONNECTED', 'Different places. Shared ideas.', 'network', '#a6b8ff', '#1e2540'),
    'NCC-': ('NCC', 'LEARN BY DOING', 'Notes, code, and new connections.', 'study', '#ffa28c', '#34231f'),
    'rescura-sync': ('Rescura Sync', 'KEEP IT CONNECTED', 'Moving parts, working together.', 'sync', '#8ee6cf', '#18332e'),
    'sce-release-management': ('Release Management', 'FROM BUILD TO SHIP', 'Every change has a journey.', 'release', '#c9ff59', '#222d1a'),
    'SEM2-Web-Pj-': ('Semester 2 · Web', 'AN EARLY EXPLORATION', 'Turning a blank page into a place.', 'web', '#ffc990', '#34271e'),
    'Sem7_CPP_Project': ('Semester 7 · C++', 'THINK IN SYSTEMS', 'Small pieces. Bigger possibilities.', 'cube', '#c4a5ff', '#2a2040'),
    'swot': ('swot', 'EDUCATION, RECOGNIZED', 'Connecting people and education.', 'education', '#90dfef', '#19313c'),
}


def shape_rect(x, y, w, h, fill, rx=12, stroke=None, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"' + (f' stroke="{stroke}"' if stroke else '') + f' {extra}/>'


def body_text(x, y, content, size, fill):
    return art.text(x,y,content,size,fill).replace(
        f'font-family="{art.SANS}"', 'font-family="Segoe UI, Arial, sans-serif"')


def spot_scene(kind, accent):
    """All scenes occupy a shared 400 × 260 artboard."""
    ink, paper = '#11191d', '#edf0e9'
    r = shape_rect
    t = art.text
    shadow = '<ellipse cx="210" cy="238" rx="157" ry="14" fill="#000" opacity=".22"/>'
    sparkle = f'<path d="m352 21 5 15 15 5-15 5-5 15-5-15-15-5 15-5Z" fill="{accent}" opacity=".8"/>'
    if kind == 'routes':
        s = r(20, 31, 350, 199, '#21372b', 18, '#4a6143')
        s += '<path d="M20 81h350M20 177h350M87 31v199M210 31v199M311 31v199" stroke="#40513c" stroke-width="16"/>'
        s += f'<path d="M87 176h123V81h101" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round"/>'
        for x, y in [(87,176), (311,81)]:
            s += f'<circle cx="{x}" cy="{y}" r="11" fill="{accent}"/><circle cx="{x}" cy="{y}" r="4" fill="{ink}"/>'
        s += r(167, 107, 87, 64, paper, 11) + f'<path d="m181 128 29-14 29 14v25l-29 12-29-12Zm29 11v26m-29-37 29 11 29-11" fill="none" stroke="#536b45" stroke-width="3"/>'
        s += r(43, 8, 144, 40, accent, 10) + t(58,34,'ON THE WAY',15,ink,700,True)
    elif kind == 'menu':
        s = '<g transform="rotate(-8 138 130)">' + r(29, 23, 187, 214, '#87523e', 13)
        s += r(21, 14, 187, 214, '#fff0da', 13) + t(43,49,'THE DAILY',16,'#633e2f',700,True)
        s += t(42,88,'MENU',35,'#3b2922',900)
        s += '<path d="M43 110h139M43 131h78m27 0h34M43 151h91m11 0h37M43 171h67m36 0h36M43 191h85m18 0h36" stroke="#bf9777" stroke-width="3" stroke-linecap="round"/></g>'
        s += f'<circle cx="285" cy="151" r="80" fill="#8b5039"/><circle cx="285" cy="142" r="80" fill="{accent}"/><circle cx="285" cy="142" r="61" fill="#f6e5cd"/><circle cx="285" cy="142" r="44" fill="#dc7e4e"/>'
        s += '<path d="M267 113q27-1 35 28-9 22-31 30-23-20-4-58" fill="#9bb37a"/><circle cx="307" cy="119" r="12" fill="#e7b65e"/><circle cx="272" cy="155" r="10" fill="#f7d8a6"/>'
    elif kind == 'parking':
        s = '<g transform="translate(24 27) matrix(1 .13 -.22 .8 22 0)">' + r(0,35,350,217,'#0e2131',16)
        s += r(0,22,350,217,'#254355',16,'#54758a')
        s += '<path d="M21 76h307M21 183h307M87 76v107M174 76v107M261 76v107" stroke="#74919f" stroke-width="3"/>'
        s += '<path d="M20 217h305" stroke="#92adb9" stroke-width="3" stroke-dasharray="22 15"/>'
        for x, color in [(103,accent),(277,'#dce7e5')]:
            s += r(x,91,55,80,'#102632',12) + r(x,83,55,80,color,12)
            s += r(x+9,98,37,24,'#254355',5) + r(x+9,138,37,11,'#254355',4)
        s += '</g>' + r(19,13,69,68,accent,14) + t(53,61,'P',44,ink,900,extra='text-anchor="middle"')
    elif kind == 'vault':
        s = r(77,49,242,183,'#4a3e68',20) + r(65,34,242,183,'#807097',20)
        s += r(83,54,205,145,'#211e35',12,accent)
        s += '<path d="M91 70h6m-6 111h6M273 70h6m-6 111h6" stroke="#d8c9ef" stroke-width="5"/>'
        s += f'<circle cx="186" cy="126" r="46" fill="#4f4368" stroke="{accent}" stroke-width="4"/><circle cx="186" cy="126" r="23" fill="#211e35"/>'
        s += f'<path d="M186 89v74m-37-37h74m-63-26 52 52m-52 0 52-52" stroke="{accent}" stroke-width="4"/>'
        s += r(22,9,126,57,paper,9) + t(85,47,'{ code }',23,'#46385f',700,True,'text-anchor="middle"')
        s += r(264,176,104,50,accent,10) + t(316,208,'SAVED',15,ink,700,True,'text-anchor="middle"')
    elif kind == 'draw':
        s = '<g transform="rotate(-5 198 122)">' + r(37,23,316,208,'#734b62',15)
        s += r(26,12,316,208,paper,15) + '<path d="M26 45h316" stroke="#d2d7d0" stroke-width="2"/>'
        s += '<path d="M57 84q30-48 64 5t64-5M58 166q23-43 60 0t65-10" fill="none" stroke="#b1c974" stroke-width="9" stroke-linecap="round"/>'
        s += '<rect x="216" y="69" width="85" height="75" rx="12" fill="#dbb4dc" transform="rotate(9 256 106)"/><circle cx="260" cy="109" r="20" fill="#af85b7"/>'
        s += f'<path d="m170 98 10 43 10-15 17-3Z" fill="{accent}" stroke="#7c3d5b" stroke-width="2"/></g>'
        for x,c in [(266,'#ffa4c5'),(300,'#9bd4e9'),(334,'#d2e58e')]:
            s += f'<circle cx="{x}" cy="223" r="21" fill="{c}" stroke="#2b2030" stroke-width="4"/><circle cx="{x}" cy="216" r="6" fill="#694a62"/><path d="M{x-10} 231q10-16 20 0" fill="#694a62"/>'
    elif kind == 'conveyor':
        s = r(17,155,365,65,'#555042',25) + r(28,166,343,43,'#171e20',20)
        for x in range(50,363,39):
            s += f'<circle cx="{x}" cy="187" r="13" fill="#747463"/><circle cx="{x}" cy="187" r="5" fill="#272d2a"/>'
        for x in [65,166,278]:
            s += r(x,104,66,50,'#cd9b59',5) + f'<path d="M{x} 104l17-16h65l-16 16Z" fill="#edc582"/><path d="M{x+32} 104v50" stroke="#f5d99b" stroke-width="6"/>'
        s += f'<path d="M183 157V37h133v120" fill="none" stroke="{accent}" stroke-width="10" stroke-linejoin="round"/>'
        s += '<path d="M244 65v91" stroke="#c9ff59" stroke-width="3" stroke-dasharray="5 5"/><path d="m227 68 17 88 17-88" fill="#c9ff59" opacity=".13"/>'
        s += r(213,18,75,41,'#182322',8) + t(251,46,'AI',24,accent,900,extra='text-anchor="middle"')
    elif kind == 'network':
        s = f'<path d="m83 75 118 113L320 69M83 75l237-6M201 188V53" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="7 6"/>'
        for x,y,color in [(23,30,'#ced7ff'),(259,26,'#dfd1ff'),(143,148,'#b4ddeb')]:
            s += r(x+5,y+9,119,83,'#364360',10) + r(x,y,119,83,color,10)
            s += f'<path d="M{x} {y+21}h119" stroke="#66799d" stroke-opacity=".4"/>'
            s += f'<path d="M{x+19} {y+43}h53m-53 17h78" stroke="#63769a" stroke-width="5" stroke-linecap="round"/>'
        s += f'<circle cx="201" cy="80" r="23" fill="{accent}"/><path d="m190 80 8 9 14-17" fill="none" stroke="{ink}" stroke-width="4"/>'
    elif kind in ('study', 'education'):
        s = '<g transform="rotate(-9 183 169)">' + r(53,150,264,63,'#c1715d',7) + r(60,149,247,48,'#f1e5d5',5)
        s += '<path d="M76 164h218m-218 13h218" stroke="#d8c7ae" stroke-width="3"/>'
        s += r(43,130,276,25,accent,6) + r(67,98,248,35,'#eed8ba',5) + '</g>'
        if kind == 'education':
            s += f'<path d="m61 75 140-62 140 62-140 62Z" fill="{accent}"/><path d="M115 99v42q86 52 172-5V99l-86 38Z" fill="#4b8395"/><path d="M332 78v74" stroke="{accent}" stroke-width="5"/><circle cx="332" cy="157" r="10" fill="{accent}"/>'
        else:
            s += '<path d="M128 25h139v104H128z" fill="#f4e9d5"/><path d="M151 50h93m-93 21h69m-69 21h83" stroke="#c1a384" stroke-width="5" stroke-linecap="round"/>'
            s += f'<path d="m298 51 12-16 17 12-12 17-55 81-18 10 2-21Z" fill="{accent}"/>'
    elif kind == 'sync':
        s = f'<path d="M107 66q105-84 200 29M295 188q-100 87-203-13" fill="none" stroke="{accent}" stroke-width="8" stroke-linecap="round"/>'
        s += f'<path d="m307 62 3 37-37-5M91 207l-3-37 37 5" fill="none" stroke="{accent}" stroke-width="8" stroke-linejoin="round"/>'
        s += r(119,72,155,133,'#335f55',22) + r(108,60,155,133,paper,22)
        s += f'<circle cx="185" cy="126" r="39" fill="{accent}"/><path d="M185 103v46m-23-23h46" stroke="#24594c" stroke-width="10" stroke-linecap="round"/>'
        s += r(272,156,96,63,accent,14) + '<path d="m292 188 15 15 28-32" fill="none" stroke="#24594c" stroke-width="6" stroke-linecap="round"/>'
    elif kind == 'release':
        s = '<path d="M51 185h89V87h119v98h94" fill="none" stroke="#778d50" stroke-width="5"/>'
        for x,y in [(51,185),(140,87),(259,185)]:
            s += r(x-25,y-25,50,50,'#2d4127',12,accent) + f'<path d="m{x-11} {y} 8 8 15-18" fill="none" stroke="{accent}" stroke-width="4"/>'
        s += '<g transform="translate(300 19) rotate(21 28 70)"><path d="M5 85Q-8 23 30 0q38 23 25 85l-25 15Z" fill="#eaf0df"/><path d="M5 57-12 86 5 83M55 57l17 29-17-3" fill="#85aa59"/>'
        s += f'<circle cx="30" cy="40" r="12" fill="{accent}" stroke="#536e36" stroke-width="4"/><path d="m19 100 11 31 11-31Z" fill="#ffbb79"/></g>'
    elif kind == 'web':
        s = r(32,37,324,192,'#74583e',15) + r(22,22,324,192,'#f8e7d2',15)
        s += '<path d="M22 56h324" stroke="#d2b99b" stroke-width="2"/>'
        for x in [42,56,70]:
            s += f'<circle cx="{x}" cy="39" r="4" fill="#b48a64"/>'
        s += r(40,73,145,119,'#e4a26b',8) + '<circle cx="112" cy="125" r="33" fill="#f7cd96"/><path d="m73 183 38-45 25 20 32-29v54" fill="#af704c"/>'
        s += r(201,77,121,13,'#b89b7c',5) + r(201,104,94,8,'#cbb197',4) + r(201,124,113,8,'#cbb197',4)
        s += r(201,156,93,31,accent,8) + t(247,177,'EXPLORE',11,'#5c3c29',700,True,'text-anchor="middle"')
    else:
        s = '<g transform="translate(97 9)"><path d="m100 0 112 63v129l-112 63L-12 192V63Z" fill="#6f5992"/>'
        s += f'<path d="m100 0 112 63-112 64L-12 63Z" fill="{accent}"/><path d="M100 127v128L-12 192V63Z" fill="#987db7"/><path d="m100 127 112-64v129l-112 63Z" fill="#594474"/>'
        s += '<path d="m100 24 69 39-69 40-69-40Z" fill="#dbc7f3"/><path d="m33 109 32 18v38l-32-18m109-6 36-20m-36 47 36-21" fill="none" stroke="#eee0ff" stroke-width="7" stroke-linejoin="round"/></g>'
    return shadow + sparkle + s


def card(repo, slot, mobile, fit_lines, write=True):
    name = repo['name']
    title, eyebrow, tagline, kind, accent, bg = PROJECTS.get(name, (
        re.sub(r'[-_]+', ' ', name).strip() or name, 'ANOTHER EXPLORATION',
        'An idea, taking shape.', 'cube', '#b9a4ff', '#241e3b'))
    featured = slot == 0 and not mobile
    w,h = (600,360) if mobile else ((1200,340) if featured else (580,360))
    uid = 'card-' + sha256(name.encode()).hexdigest()[:9]
    content = f'''<defs>
<radialGradient id="{uid}-glow" cx="85%" cy="20%" r="80%"><stop stop-color="{accent}" stop-opacity=".12"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<pattern id="{uid}-dots" width="23" height="23" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".8" fill="{accent}" opacity=".12"/></pattern>
</defs>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="{bg}" stroke="{accent}" stroke-opacity=".18"/>
<rect width="{w}" height="{h}" rx="22" fill="url(#{uid}-glow)"/>
<rect width="{w}" height="{h}" rx="22" fill="url(#{uid}-dots)"/>
<path d="M30 24h26" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
'''
    content += art.text(30,51,eyebrow,14,accent,700,True,extra='letter-spacing="1.5"')
    text_width = 505 if featured and not mobile else 510
    max_size = 68 if featured else 46
    lines, size = fit_lines(title, text_width, 135 if featured else 103, max_size)
    for index,line in enumerate(lines):
        content += art.text(28,105+index*size*1.06,line,size,'#f4f4ed',800,extra='letter-spacing="-1.5"')
    if featured and not mobile:
        content += body_text(31,245,tagline,21,'#b9c5bb')
        sx,sy,scale = 680,32,1.05
    elif featured:
        content += body_text(31,238,tagline,20,'#b9c5bb')
        sx,sy,scale = 92,260,1
    else:
        for index,line in enumerate(textwrap.wrap(tagline,22)):
            content += body_text(30,202+index*24,line,19 if mobile else 17,'#bac4c2')
        sx,sy,scale = 285,158,.65
    content += f'<g transform="translate({sx} {sy}) scale({scale})"><g class="scene-float">{spot_scene(kind,accent)}</g></g>'
    language = repo.get('language') or ('Fork' if repo.get('fork') else 'Project')
    chip_y = h-49
    chip_width = max(82, len(language)*10+30)
    content += shape_rect(29,chip_y,chip_width,29,'#10191b',8,accent,extra='stroke-opacity=".28"')
    content += art.text(44,chip_y+20,language,15,accent,600,True)
    content += f'<circle cx="{w-40}" cy="{h-35}" r="15" fill="{accent}" fill-opacity=".12"/><path d="m{w-45} {h-30} 10-10m-10 0h10v10" fill="none" stroke="{accent}" stroke-width="2"/>'
    filename = f"build-{slot+1}{'-mobile' if mobile else ''}.svg"
    svg = art.svg(filename,w,h,title+' / '+eyebrow,content,write=write)
    return filename if write else svg
