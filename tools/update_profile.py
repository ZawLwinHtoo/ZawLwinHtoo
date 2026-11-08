"""Sync public GitHub metadata into the profile. Python standard library only."""
import argparse
from datetime import datetime, timezone
from html import escape
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

ROOT = Path(__file__).resolve().parents[1]
OWNER = "ZawLwinHtoo"
INTERVAL = 30 * 60
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


def select_projects(repos, now):
    if not repos:
        return []
    offset = (int(now.timestamp()) // INTERVAL * 3) % len(repos)
    return [repos[(offset + i) % len(repos)] for i in range(min(3, len(repos)))]


def wrapped(value, width):
    return textwrap.wrap(clean(value), width=width, break_long_words=True,
                         break_on_hyphens=False, replace_whitespace=True)


def fit_lines(value, width, height, largest=134, smallest=18):
    for size in range(largest, smallest - 1, -1):
        lines = wrapped(value, max(1, int(width / (size * .76))))
        if len(lines) * size * 1.06 <= height:
            return lines, size
    raise ValueError("Text exceeds the supported profile bio length")


def banner(profile, mobile=False):
    # Keep the original circuit artwork, replacing all identity/headline text.
    art.hero(mobile=mobile)
    filename = "profile-banner-mobile.svg" if mobile else "profile-banner.svg"
    tree = ET.parse(art.ASSETS / filename)
    root = tree.getroot()
    name = clean(profile.get("name")) or profile["login"]
    bio = clean(profile.get("bio"))
    root.find("s:title", NS).text = name + (" / " + bio if bio else "")
    identity = root.find(".//s:g[@id='identity']/s:text", NS)
    identity.text = name.upper()
    identity.set("font-size", str(min(20, 440 / max(1, len(name) * .65))))
    for parent in root.iter():
        for node in list(parent):
            if node.tag == "{" + NS["s"] + "}text" and clean(node.text) in ("ENJOY", "BUGS."):
                parent.remove(node)
    x, top, width, height = (30, 88, 540, 190) if mobile else (44, 95, 560, 265)
    # An empty bio displays the current name rather than an outdated slogan.
    lines, size = fit_lines((bio or name).upper(), width, height, 112 if mobile else 134)
    start = top + (height - len(lines) * size * 1.06) / 2 + size * .86
    for index, line in enumerate(lines):
        node = ET.fromstring(art.text(x, round(start + index * size * 1.06, 1), line,
                                     size, art.CREAM if index % 2 == 0 else art.LIME, 900))
        node.tag = "{" + NS["s"] + "}text"
        root.append(node)
    for node in root.findall(".//s:text", NS):
        if clean(node.text).startswith("@ZawLwinHtoo"):
            node.text = "@" + profile["login"]
        elif clean(node.text) == "CURIOUS BY DEFAULT":
            node.text = "GITHUB / PROFILE"
    ET.register_namespace("", NS["s"])
    tree.write(art.ASSETS / filename, encoding="unicode", xml_declaration=False)


def project_title(repo):
    return clean(repo["name"].replace("-", " ").replace("_", " ")) or repo["name"]


def project_card(repo, slot, mobile=False):
    # Preserve the three bespoke illustrations for their matching repositories.
    originals = {"lannpya-ai": "project-lannpya", "menu-maker": "project-menu",
                 "parking-management-system": "project-parking"}
    if repo["name"] in originals:
        base = originals[repo["name"]]
        suffix = "-mobile" if mobile and repo["name"] == "lannpya-ai" else ""
        return base + suffix + ".svg"
    large = slot == 0
    w, h = (600, 550) if large and mobile else ((1200, 340) if large else (580, 360))
    accent, bg = [(art.LIME, "#192218"), ("#ffb184", "#29201b"),
                  ("#89d5ff", "#172532")][slot]
    title = project_title(repo)
    text_width = 540 if mobile or not large else 580
    lines, size = fit_lines(title, text_width - 50, 145, 70 if large else 59)
    content = f'<rect width="{w}" height="{h}" rx="18" fill="{bg}"/>'
    label = clean(repo.get("language")) or ("FORK" if repo.get("fork") else "PROJECT")
    content += art.text(30, 44, f"{slot + 1:02} / {label.upper()}", 18, accent, mono=True)
    for i, line in enumerate(lines):
        content += art.text(28, 108 + i * size * 1.06, line, size, weight=900)
    # Original terminal illustration for every other repository.
    gx, gy, scale = (735, 68, 1) if large and not mobile else ((280, 302, .75) if large else (349, 202, .65))
    content += f'''<g transform="translate({gx} {gy}) scale({scale})">
<rect width="320" height="196" rx="12" fill="{art.INK}" stroke="{accent}" stroke-opacity=".4"/>
<path d="M0 34h320" stroke="{accent}" stroke-opacity=".25"/>
<g fill="{accent}"><circle cx="18" cy="17" r="4"/><circle cx="34" cy="17" r="4"/><circle cx="50" cy="17" r="4"/></g>
<path d="m34 78 24 22-24 22m47 0h45M34 155h112m18 0h56" fill="none" stroke="{accent}" stroke-width="6"/>
</g>'''
    tags = []
    if repo.get("fork"):
        tags.append("FORK")
    if repo.get("archived"):
        tags.append("ARCHIVED")
    tags.append("OPEN REPOSITORY")
    content += art.text(30, h - 30, " / ".join(tags), 17, accent, mono=True)
    filename = f"build-{slot + 1}{'-mobile' if mobile else ''}.svg"
    art.svg(filename, w, h, title + " / " + label, content)
    return filename


def description(repo):
    return clean(repo.get("description")) or ("A forked repository." if repo.get("fork") else "Explore the code and project files.")


def build_markup(repo, slot):
    url = f'https://github.com/{repo["owner"]["login"]}/{repo["name"]}'
    title = escape(project_title(repo))
    card = project_card(repo, slot)
    if slot == 0:
        mobile = project_card(repo, slot, mobile=True)
        image = (f'<picture>\n  <source media="(max-width: 600px)" srcset="assets/{mobile}">\n'
                 f'  <img src="assets/{card}" alt="{title}. Open the repository." width="100%">\n</picture>')
    else:
        image = f'<img src="assets/{card}" alt="{title}. Open the repository." width="100%">'
    return (f'<a href="{url}">\n{image}\n</a>\n\n<p><b>{title}</b><br>\n'
            f'{escape(description(repo))}</p>\n\n<p><a href="{url}">Explore the project →</a></p>')


def generate(profile, repos, now):
    if profile.get("login", "").casefold() != OWNER.casefold():
        raise ValueError("Refusing to generate a different user's profile")
    projects = public_projects(repos, profile["login"])
    selected = select_projects(projects, now)
    art.ASSETS.mkdir(exist_ok=True)
    banner(profile)
    banner(profile, mobile=True)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    name = escape(clean(profile.get("name")) or profile["login"])
    bio = escape(clean(profile.get("bio")))
    # Avoid stale biography text and stale image alt text after a profile edit.
    readme = re.sub(r'alt="[^"]*"(?= width="100%">\n</picture>)',
                    lambda _: 'alt="' + escape(clean(profile.get("name")) or profile["login"], quote=True) + '. ' + bio + '"',
                    readme, count=1)
    introduction = f'<p align="center">\n  <b>Hi, I\'m {name}.</b>'
    if bio:
        introduction += f'<br>\n  {bio}'
    introduction += '\n</p>'
    readme = re.sub(r'<p align="center">.*?</p>', lambda _: introduction, readme, count=1, flags=re.S)
    blocks = [build_markup(repo, i) for i, repo in enumerate(selected)]
    builds = "## Selected builds\n\n"
    builds += (f'Three at a time, rotating through {len(projects)} public repositories. '
               'Refreshes automatically about every 30 minutes.\n\n')
    if blocks:
        builds += blocks[0] + "\n\n"
        if len(blocks) > 1:
            builds += '<table>\n<tr>\n' + '\n'.join(
                f'<td width="50%" valign="top">\n\n{block}\n\n</td>' for block in blocks[1:])
            builds += '\n</tr>\n</table>\n\n'
    else:
        builds += "New builds will appear here when a public repository is available.\n\n"
    readme = re.sub(r'## Selected builds\n.*?(?=## The toolbox)', lambda _: builds + '<br>\n\n', readme, flags=re.S)
    (ROOT / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    for asset in art.ASSETS.glob("*.svg"):
        ET.parse(asset)
    print(f"Synced {profile['login']}: {len(projects)} public projects; showing "
          + ", ".join(r["name"] for r in selected))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, help="Use a local metadata snapshot for offline verification")
    parser.add_argument("--at", help="ISO UTC timestamp to preview another rotation")
    args = parser.parse_args()
    now = datetime.fromisoformat(args.at.replace("Z", "+00:00")) if args.at else datetime.now(timezone.utc)
    if args.snapshot:
        data = json.loads(args.snapshot.read_text(encoding="utf-8"))
        profile, repos = data["profile"], data["repos"]
    else:
        profile, repos = fetch_metadata(OWNER)
    generate(profile, repos, now)
