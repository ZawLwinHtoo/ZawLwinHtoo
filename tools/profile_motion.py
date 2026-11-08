"""Self-contained SVG illustrations and a GitHub-compatible CSS carousel."""
from hashlib import sha256
import re
import xml.etree.ElementTree as ET

import generate_artwork as art


def bio_theme(bio):
    words = set(re.findall(r"[\w]+", bio.casefold()))
    themes = [
        ("bugs", {"bug", "bugs", "debug", "debugging"}),
        ("ai", {"ai", "ml", "neural", "intelligence", "robot", "robotics"}),
        ("code", {"code", "coding", "developer", "software", "programmer", "programming", "building"}),
        ("web", {"web", "website", "frontend", "backend", "fullstack"}),
        ("music", {"music", "guitar", "piano", "sing", "singing"}),
        ("nature", {"nature", "plant", "plants", "garden", "grow", "growing"}),
        ("games", {"game", "games", "gaming", "gamer"}),
        ("space", {"space", "rocket", "stars", "astronaut"}),
        ("study", {"study", "studying", "student", "learn", "learning", "learner", "reading", "knowledge", "curious", "curiosity", "books", "book", "education"}),
        ("love", {"love", "heart", "happy", "happiness"}),
        ("hello", {"hi", "hello", "hey", "welcome", "mingalabar"}),
    ]
    return next((theme for theme, keywords in themes if words & keywords), "identity")


def bio_figure(bio, x, y, scale=1):
    theme = bio_theme(bio)
    if theme == "bugs":
        return theme, art.bug(x, y, scale)
    fill = art.LIME
    common = f'fill="none" stroke="{fill}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
    if theme == "hello":
        shape = f'''<g class="bio-wave" fill="{fill}">
<rect x="-47" y="-83" width="21" height="117" rx="10"/>
<rect x="-23" y="-106" width="21" height="140" rx="10"/>
<rect x="1" y="-99" width="21" height="133" rx="10"/>
<rect x="25" y="-77" width="21" height="111" rx="10"/>
<rect x="-47" y="-10" width="93" height="106" rx="40"/>
<rect x="-76" y="-4" width="27" height="89" rx="13" transform="rotate(-35 -62 40)"/>
<path d="M-30 80h60v37h-60z"/>
<path d="M-18 26q39 0 41 38" fill="none" stroke="{art.INK}" stroke-width="5"/>
</g><g {common} opacity=".65"><path d="M-101-59q-25 30-12 62M-119-78q-35 41-21 86M86-98q26 26 23 58M107-117q36 35 32 81"/></g>'''
    elif theme == "code":
        shape = f'''<rect x="-125" y="-87" width="250" height="174" rx="16" {common}/>
<path d="M-125-48h250m-206 42 31 28-31 28m55 0h53" {common}/>
<g fill="{fill}"><circle cx="-102" cy="-68" r="5"/><circle cx="-82" cy="-68" r="5"/><circle cx="-62" cy="-68" r="5"/>
<rect class="bio-cursor" x="50" y="42" width="24" height="8"/></g>'''
    elif theme == "ai":
        shape = f'''<rect x="-78" y="-78" width="156" height="156" rx="25" {common}/>
<path d="M-48-108v30M0-108v30M48-108v30M-48 78v30M0 78v30M48 78v30M-108-48h30M-108 0h30M-108 48h30M78-48h30M78 0h30M78 48h30" {common}/>
{art.text(0, 25, 'AI', 75, fill, 900, extra='text-anchor="middle"')}
<circle class="bio-pulse" r="108" fill="none" stroke="{fill}" opacity=".3"/>'''
    elif theme == "web":
        shape = f'''<g {common}><circle r="105"/><ellipse rx="48" ry="105"/>
<path d="M-99-34H99M-99 34H99M-105 0h210"/></g>'''
    elif theme == "music":
        shape = f'''<g {common}><path d="M-40 67V-69l137-27V40M-40-37 97-64"/>
<ellipse cx="-65" cy="70" rx="28" ry="20"/><ellipse cx="72" cy="43" rx="28" ry="20"/>
<path class="bio-pulse" d="M-111-50q-24 30 0 61M-128-69q-41 49 0 99"/></g>'''
    elif theme == "nature":
        shape = f'''<g {common}><path d="M0 111V-35M0 28Q-111 20-97-70 0-60 0 28ZM0-8Q2-94 100-102 113-21 0-8Z"/>
<path d="M-48-21 0 28M48-58 0-8M-48 111h96"/></g>'''
    elif theme == "games":
        shape = f'''<path d="M-72-55H72q30 0 44 52l17 61q10 47-31 40L52 56H-52l-50 42q-41 7-31-40l17-61q14-52 44-52Z" {common}/>
<path d="M-78-3v48M-102 21h48" {common}/>
<g fill="{fill}"><circle cx="71" cy="7" r="10"/><circle cx="98" cy="31" r="10"/></g>'''
    elif theme == "space":
        shape = f'''<g {common}><path d="M-33 35Q-71-57 46-111 98 6 13 60ZM-33-5q-58-4-67 61l67-21M38 45q13 50-45 81L13 60"/>
<circle cx="17" cy="-39" r="20"/><path class="bio-pulse" d="M-49 70-77 102M-30 82-45 111"/></g>'''
    elif theme == "study":
        shape = f'''<ellipse cx="0" cy="116" rx="132" ry="16" fill="{fill}" opacity=".08"/>
<path d="M0-47q-64-43-125-13V95q67-25 125 14 58-39 125-14V-60Q64-90 0-47Z" fill="#293925" stroke="{fill}" stroke-width="4"/>
<path d="M0-60q-55-38-112-16V78q59-20 112 17 53-37 112-17V-76Q55-98 0-60Z" fill="#f4f4e8"/>
<path d="M0-59V94M-85-41q31-8 60 7M-85-11q31-8 60 7M-85 19q31-8 60 7M25-34q29-15 60-7M25-4q29-15 60-7M25 26q29-15 60-7" fill="none" stroke="#657b55" stroke-width="4" stroke-linecap="round"/>
<path d="M63-88v53l13-11 13 8v-51" fill="{fill}"/>
<g class="bio-pulse" fill="{fill}"><path d="m-79-130 5 14 15 5-15 5-5 14-5-14-15-5 15-5Z"/><path d="m52-147 4 11 12 4-12 4-4 11-4-11-12-4 12-4Z"/></g>'''
    elif theme == "love":
        shape = f'''<path class="bio-pulse" d="M0 100-100-3Q-148-70-79-96-29-113 0-65 29-113 79-96 148-70 100-3Z" fill="{fill}"/>
<path d="M-62-68q-25 5-23 29" fill="none" stroke="{art.INK}" stroke-width="7" stroke-linecap="round"/>'''
    else:
        # An unknown topic gets artwork made from the current bio, never a stale bug.
        initials = ''.join(re.findall(r'\w', bio)[:2]).upper() or 'Z'
        angle = int(sha256(bio.encode()).hexdigest()[:4], 16) % 90
        shape = f'''<g transform="rotate({angle})" {common} opacity=".55"><rect x="-95" y="-95" width="190" height="190" rx="35"/></g>
<circle r="76" fill="{art.INK}" stroke="{fill}" stroke-width="2"/>
{art.text(0, 26, initials, 76, fill, 900, extra='text-anchor="middle"')}'''
    return theme, f'<g id="bio-illustration" data-theme="{theme}" transform="translate({x} {y}) scale({scale})">{shape}</g>'


def carousel(projects, card_for, mobile=False):
    """Embed all artwork; CSS slides the viewport without JavaScript or fetches."""
    width, height = (600, 1180) if mobile else (1200, 790)
    groups = [projects[i:i + 3] for i in range(0, len(projects), 3)]
    if not groups:
        art.svg('build-carousel-mobile.svg' if mobile else 'build-carousel.svg', width, height,
                'Project showcase', art.text(30, 90, 'New projects coming soon.', 32))
        return
    # Complete the last page with projects from the beginning; no duplicate per page.
    if len(projects) >= 3 and len(groups[-1]) < 3:
        groups[-1] += projects[:3 - len(groups[-1])]
    count = len(groups)
    duration = count * 6
    stops = []
    for index in range(count):
        begin = index / count * 100
        hold = (index + 1) / count * 100 - .5 / duration * 100
        stops += [f'{begin:.6f}%,{hold:.6f}%{{transform:translateX(-{index * width}px)}}']
    stops.append(f'100%{{transform:translateX(-{count * width}px)}}')
    css = f'''<defs><clipPath id="carousel-window"><rect width="{width}" height="{height}" rx="18"/></clipPath></defs>
<style>
.carousel-track{{animation:project-slide {duration}s linear infinite}}
@keyframes project-slide{{{''.join(stops)}}}
.carousel-progress{{animation:project-progress 6s linear infinite;transform-origin:0 0}}
@keyframes project-progress{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.scene-float{{animation:scene-drift 5s ease-in-out infinite}}
@keyframes scene-drift{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
@media(prefers-reduced-motion:reduce){{.carousel-track,.carousel-progress,.scene-float{{animation:none}}}}
</style>
<rect width="{width}" height="{height}" rx="18" fill="{art.INK}"/>
<g clip-path="url(#carousel-window)"><g class="carousel-track">'''
    panels = []
    for page, group in enumerate(groups):
        content = ''
        for slot, repo in enumerate(group):
            name = card_for(repo, slot, mobile=mobile)
            root = ET.parse(art.ASSETS / name).getroot()
            x, y, w, h = (0, slot * 384, 600, 360) if mobile else (
                (0, 0, 1200, 340) if slot == 0 else ((slot - 1) * 612, 364, 588, 360))
            root.attrib.update(x=str(x), y=str(y), width=str(w), height=str(h))
            root.set('data-repository', repo['name'])
            # Unique IDs keep embedded original artwork independent across slides.
            serialized = ET.tostring(root, encoding='unicode')
            suffix = f'-p{page}-s{slot}'
            ids = re.findall(r'\bid="([^"]+)"', serialized)
            for identifier in ids:
                serialized = serialized.replace(f'id="{identifier}"', f'id="{identifier}{suffix}"')
                serialized = serialized.replace(f'url(#{identifier})', f'url(#{identifier}{suffix})')
                serialized = serialized.replace(f'aria-labelledby="{identifier}"', f'aria-labelledby="{identifier}{suffix}"')
            content += serialized
        content += art.text(18, height - 23, f'{page + 1:02} / {count:02}   NEXT PROJECTS IN 6s', 17 if mobile else 20, art.MUTED, mono=True)
        content += f'<rect class="carousel-progress" x="0" y="{height - 5}" width="{width}" height="3" fill="{art.LIME}"/>'
        panels.append(content)
    for index, panel in enumerate(panels + panels[:1]):
        if index == count:
            for identifier in re.findall(r'\bid="([^"]+)"', panel):
                panel = panel.replace(f'id="{identifier}"', f'id="{identifier}-loop"')
                panel = panel.replace(f'url(#{identifier})', f'url(#{identifier}-loop)')
                panel = panel.replace(f'aria-labelledby="{identifier}"', f'aria-labelledby="{identifier}-loop"')
        css += f'<g class="carousel-panel" transform="translate({index * width} 0)">{panel}</g>'
    css += '</g></g>'
    filename = 'build-carousel-mobile.svg' if mobile else 'build-carousel.svg'
    art.svg(filename, width, height, 'Rotating projects / three cards / new slide every six seconds', css)
