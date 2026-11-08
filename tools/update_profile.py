"""Sync public GitHub metadata into the profile. Python standard library only."""
import argparse
from html import escape
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import textwrap
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

import generate_artwork as art
import profile_motion as motion
import project_art

ROOT = Path(__file__).resolve().parents[1]
OWNER = "ZawLwinHtoo"
PRIORITY = {"lannpya-ai": 0, "menu-maker": 1, "parking-management-system": 2}
NS = {"s": "http://www.w3.org/2000/svg"}


def clean(value):
    return " ".join(str(value or "").split())


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-profile-sync"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    request = urllib.request.Request("https://api.github.com" + path, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except urllib.error.URLError:
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)


def fetch_metadata(owner):
    profile = api(f"/users/{owner}")
    repos = []
    for page in range(1, 1000):
        batch = api(f"/users/{owner}/repos?type=owner&sort=full_name&per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
    return profile, repos


def public_projects(repos, owner):
    # Include forks and archived projects, but never expose private repositories.
    return sorted((r for r in repos if not r.get("private", False)
                   and r.get("owner", {}).get("login", "").casefold() == owner.casefold()
                   and r["name"].casefold() != owner.casefold()),
                  key=lambda r: (PRIORITY.get(r["name"], 3), r["name"].casefold()))


def wrapped(value, width):
    # Keep normal words intact; only split unusually long unbroken strings.
    split_long = max((len(word) for word in clean(value).split()), default=0) > 32
    return textwrap.wrap(clean(value), width=width, break_long_words=split_long,
                         break_on_hyphens=False, replace_whitespace=True)


def fit_lines(value, width, height, largest=134, smallest=18):
    for size in range(largest, smallest - 1, -1):
        columns = max(1, int(width / (size * .76)))
        lines = wrapped(value, columns)
        if all(len(line) <= columns for line in lines) and len(lines) * size * 1.06 <= height:
            return lines, size
    raise ValueError("Text exceeds the supported profile bio length")


def render_banner(profile, mobile=False):
    # Retain the layout, but match both the headline and illustration to the bio.
    root = ET.fromstring(art.hero(mobile=mobile, write=False))
    name = clean(profile.get("name")) or profile["login"]
    bio = clean(profile.get("bio"))
    theme, illustration = motion.bio_figure(bio or name, 309 if mobile else 884,
                                          485 if mobile else 245, .76 if mobile else .95)
    root.find("s:title", NS).text = name + (" / " + bio if bio else "")
    identity = root.find(".//s:g[@id='identity']/s:text", NS)
    identity.text = name.upper()
    identity.set("font-size", str(min(20, 440 / max(1, len(name) * .65))))
    for parent in root.iter():
        for node in list(parent):
            if node.get("id") == "circuit-beetle":
                parent.remove(node)
            if node.tag == "{" + NS["s"] + "}text" and clean(node.text) in ("ENJOY", "BUGS."):
                parent.remove(node)
    figure = ET.fromstring(illustration)
    for node in figure.iter():
        node.tag = "{" + NS["s"] + "}" + node.tag
    root.append(figure)
    root.find("s:style", NS).text += '''
.bio-wave{animation:hello-wave 2.4s ease-in-out infinite;transform-origin:0px 55px}
@keyframes hello-wave{0%,60%,100%{transform:rotate(0deg)}15%,35%{transform:rotate(13deg)}25%,45%{transform:rotate(-10deg)}}
.bio-cursor{animation:cursor-blink 1s step-end infinite}
@keyframes cursor-blink{50%{opacity:0}}
.bio-pulse{animation:bio-pulse 3s ease-in-out infinite;transform-origin:0 0}
@keyframes bio-pulse{0%,100%{opacity:.65}50%{opacity:1}}
@media(prefers-reduced-motion:reduce){.bio-wave,.bio-cursor,.bio-pulse{animation:none}}
'''
    x, top, width, height = (30, 88, 540, 190) if mobile else (44, 95, 560, 265)
    # An empty bio displays the current name rather than an outdated slogan.
    lines, size = fit_lines(bio or name, width, height, 112 if mobile else 134)
    start = top + (height - len(lines) * size * 1.06) / 2 + size * .86
    for index, line in enumerate(lines):
        node = ET.fromstring(art.text(x, round(start + index * size * 1.06, 1), line,
                                     size, art.CREAM if index % 2 == 0 else art.LIME, 900,
                                     extra='data-bio-line="true"'))
        node.tag = "{" + NS["s"] + "}text"
        root.append(node)
    for node in root.findall(".//s:text", NS):
        if clean(node.text).startswith("@ZawLwinHtoo"):
            node.text = "@" + profile["login"]
        elif clean(node.text) == "CURIOUS BY DEFAULT":
            node.text = "GITHUB / PROFILE"
        elif clean(node.text) == "BUG / 001":
            node.text = theme.upper() + " / 001"
        elif theme != "bugs" and clean(node.text) == "CODE. BREAK. LEARN. REPEAT.":
            node.text = "SAY HELLO. KEEP EXPLORING." if theme == "hello" else "CREATE. EXPLORE. KEEP GOING."
    ET.register_namespace("", NS["s"])
    return ET.tostring(root, encoding="unicode")


def banner(profile, mobile=False):
    filename = "profile-banner-mobile.svg" if mobile else "profile-banner.svg"
    (art.ASSETS / filename).write_text(render_banner(profile, mobile), encoding="utf-8", newline="\n")


def project_title(repo):
    return clean(repo["name"].replace("-", " ").replace("_", " ")) or repo["name"]


def project_card(repo, slot, mobile=False):
    return project_art.card(repo, slot, mobile, fit_lines)


def description(repo):
    return clean(repo.get("description")) or ("A forked repository." if repo.get("fork") else "Explore the code and project files.")


def generate(profile, repos):
    if profile.get("login", "").casefold() != OWNER.casefold():
        raise ValueError("Refusing to generate a different user's profile")
    projects = public_projects(repos, profile["login"])
    art.ASSETS.mkdir(exist_ok=True)
    banner(profile)
    banner(profile, mobile=True)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    name = escape(clean(profile.get("name")) or profile["login"])
    bio = escape(clean(profile.get("bio")))
    configuration = ROOT / 'live-profile.json'
    live_url = json.loads(configuration.read_text())['banner_url'] if configuration.exists() else None
    if live_url:
        desktop_source = escape(live_url + '?v=4', quote=True)
        mobile_source = escape(live_url + '?mobile=1&v=4', quote=True)
        banner_alt = 'Current GitHub bio with its matching animated illustration'
        introduction = ''
    else:
        desktop_source, mobile_source = 'assets/profile-banner.svg', 'assets/profile-banner-mobile.svg'
        banner_alt = name + '. ' + bio
        introduction = f'<p align="center">\n  <b>Hi, I\'m {name}.</b><br>\n  {bio}\n</p>\n\n'
    header = f'''<picture>
  <source media="(max-width: 600px)" srcset="{mobile_source}">
  <img src="{desktop_source}" alt="{banner_alt}" width="100%">
</picture>

{introduction}<p align="center">
  <a href="#selected-builds">Selected builds</a> &nbsp; / &nbsp;
  <a href="#the-toolbox">The toolbox</a> &nbsp; / &nbsp;
  <a href="https://github.com/{profile['login']}?tab=repositories">All repositories ↗</a>
</p>

'''
    readme = re.sub(r'\A.*?(?=## Selected builds)', lambda _: header, readme, flags=re.S)
    motion.carousel(projects, project_card)
    motion.carousel(projects, project_card, mobile=True)
    builds = "## Selected builds\n\n"
    builds += (f'Three at a time. All {len(projects)} public projects. A new slide every six seconds.\n\n')
    if projects:
        builds += '''<picture>
  <source media="(max-width: 600px)" srcset="assets/build-carousel-mobile.svg">
  <img src="assets/build-carousel.svg" alt="Animated project showcase. Three cards slide to the next projects every six seconds. Repository links are below." width="100%">
</picture>

<details>
<summary>Open a repository</summary>

'''
        for repo in projects:
            url = f'https://github.com/{profile["login"]}/{repo["name"]}'
            builds += f'<p><a href="{url}"><b>{escape(project_title(repo))}</b></a> — {escape(description(repo))}</p>\n\n'
        builds += '</details>\n\n'
    else:
        builds += "New builds will appear here when a public repository is available.\n\n"
    readme = re.sub(r'## Selected builds\n.*?(?=## The toolbox)', lambda _: builds + '<br>\n\n', readme, flags=re.S)
    # A changed image receives a new URL so GitHub/browser caches fetch its new content.
    def versioned(match):
        asset = art.ASSETS / match.group(2)
        version = sha256(asset.read_text(encoding='utf-8').encode('utf-8')).hexdigest()[:12]
        return f'{match.group(1)}="assets/{match.group(2)}?v={version}"'
    readme = re.sub(r'(src|srcset)="assets/([^"?]+\.svg)(?:\?[^\"]*)?"', versioned, readme)
    (ROOT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    for asset in art.ASSETS.glob("*.svg"):
        ET.parse(asset)
    print(f"Synced {profile['login']}: bio theme={motion.bio_theme(clean(profile.get('bio')))}; "
          f"{len(projects)} projects in six-second animated slides")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, help="Use a local metadata snapshot for offline verification")
    args = parser.parse_args()
    if args.snapshot:
        data = json.loads(args.snapshot.read_text(encoding="utf-8"))
        profile, repos = data["profile"], data["repos"]
    else:
        profile, repos = fetch_metadata(OWNER)
    generate(profile, repos)
