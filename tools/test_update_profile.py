from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import update_profile as sync


def repo(name, **extra):
    return {"name": name, "owner": {"login": sync.OWNER}, "private": False,
            "language": "Python", "description": None, **extra}


class ProfileTests(unittest.TestCase):
    def test_only_owned_public_projects_with_forks_and_archives(self):
        values = [repo("public"), repo("private", private=True), repo(sync.OWNER),
                  repo("fork", fork=True), repo("archive", archived=True),
                  repo("other", owner={"login": "someone-else"})]
        self.assertEqual({r["name"] for r in sync.public_projects(values, sync.OWNER)},
                         {"public", "fork", "archive"})

    def test_pagination_does_not_stop_at_one_hundred_repositories(self):
        profile = {"login": sync.OWNER}
        with patch.object(sync, "api", side_effect=[profile, [repo(str(i)) for i in range(100)], [repo("last")]]) as api:
            result, repos = sync.fetch_metadata(sync.OWNER)
        self.assertEqual(result, profile)
        self.assertEqual(len(repos), 101)
        self.assertIn("page=2", api.call_args.args[0])

    def test_generation_updates_bio_name_links_and_is_repeatable(self):
        source = sync.ROOT
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            assets = root / "assets"
            shutil.copytree(source / 'assets', assets)
            (root / "README.md").write_text((source / "README.md").read_text(encoding="utf-8"), encoding="utf-8")
            profile = {"login": sync.OWNER, "name": 'Zaw <&> "Htoo"', "bio": 'Build <things> & learn "daily"!'}
            projects = [repo("a-project", description="A <tool> & more"), repo("b-project"), repo("c-project")]
            with patch.object(sync, "ROOT", root), patch.object(sync.art, "ASSETS", assets):
                sync.generate(profile, projects)
                first = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                sync.generate(profile, projects)
                self.assertEqual(first, {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()})
                readme = (root / "README.md").read_text(encoding="utf-8")
                self.assertIn("&lt;things&gt; &amp; learn &quot;daily&quot;!", readme)
                self.assertNotIn("one experiment at a time", readme)
                for project in projects:
                    self.assertIn(f'https://github.com/{sync.OWNER}/{project["name"]}', readme)
                for path in assets.glob("*.svg"):
                    ET.parse(path)
                for filename in ("profile-banner.svg", "profile-banner-mobile.svg"):
                    title = ET.parse(assets / filename).getroot().find("s:title", sync.NS).text
                    self.assertIn(profile["bio"], title)
                profile["bio"] = None
                sync.generate(profile, [])
                self.assertNotIn("daily", (root / "README.md").read_text(encoding="utf-8"))
                self.assertNotIn("BUGS", (assets / "profile-banner.svg").read_text(encoding="utf-8"))

    def test_long_unicode_bio_fits_without_losing_text(self):
        for value in ["W" * 160, "Build useful things & learn every day. " * 4,
                      "မြန်မာစာ စမ်းသပ်ခြင်း " * 7, "こんにちは世界 " * 15]:
            lines, size = sync.fit_lines(value, 540, 190, largest=112)
            self.assertLessEqual(len(lines) * size * 1.06, 190)
            self.assertEqual("".join(lines).replace(" ", ""), sync.clean(value).replace(" ", ""))

    def test_bio_changes_both_artwork_and_cached_image_url(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            assets = root / "assets"
            shutil.copytree(sync.ROOT / 'assets', assets)
            (root / "README.md").write_text((sync.ROOT / "README.md").read_text(encoding="utf-8"), encoding="utf-8")
            with patch.object(sync, 'ROOT', root), patch.object(sync.art, 'ASSETS', assets):
                profile = {'login': sync.OWNER, 'name': 'Zaw', 'bio': 'Enjoy bugs!!!'}
                sync.generate(profile, [repo('a')])
                previous = (root / 'README.md').read_text(encoding='utf-8')
                self.assertIn('circuit-beetle', (assets / 'profile-banner.svg').read_text(encoding='utf-8'))
                profile['bio'] = 'hi'
                sync.generate(profile, [repo('a')])
                current = (root / 'README.md').read_text(encoding='utf-8')
                for filename in ['profile-banner.svg', 'profile-banner-mobile.svg']:
                    svg = (assets / filename).read_text(encoding='utf-8')
                    self.assertIn('data-theme="hello"', svg)
                    self.assertNotIn('circuit-beetle', svg)
                    self.assertIn('hello-wave', svg)
                self.assertNotEqual(previous.split('profile-banner.svg?v=')[1][:12],
                                    current.split('profile-banner.svg?v=')[1][:12])
                self.assertIn('hi', current)
                self.assertNotIn('Enjoy bugs!!!', current)

    def test_carousel_contains_every_project_and_has_unique_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(sync.art, 'ASSETS', Path(folder)):
                for count in [0, 1, 2, 3, 4, 13, 101]:
                    projects = [repo(f'project-{index}') for index in range(count)]
                    for mobile in [False, True]:
                        sync.motion.carousel(projects, sync.project_card, mobile=mobile)
                        path = Path(folder) / ('build-carousel-mobile.svg' if mobile else 'build-carousel.svg')
                        tree = ET.parse(path)
                        names = {node.get('data-repository') for node in tree.iter() if node.get('data-repository')}
                        self.assertEqual(names, {r['name'] for r in projects})
                        ids = [node.get('id') for node in tree.iter() if node.get('id')]
                        self.assertEqual(len(ids), len(set(ids)))
                        for panel in tree.findall('.//s:g[@class="carousel-panel"]', sync.NS):
                            cards = [node.get('data-repository') for node in panel if node.get('data-repository')]
                            self.assertEqual(len(cards), min(count, 3))
                            self.assertEqual(len(cards), len(set(cards)))
                        if count:
                            self.assertIn('prefers-reduced-motion:reduce', path.read_text(encoding='utf-8'))

    def test_live_readme_does_not_embed_a_stale_bio_or_depend_on_bio_commits(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            assets = root / 'assets'
            shutil.copytree(sync.ROOT / 'assets', assets)
            (root / 'README.md').write_text((sync.ROOT / 'README.md').read_text(encoding='utf-8'), encoding='utf-8')
            (root / 'live-profile.json').write_text('{"banner_url":"https://example.com/api/banner"}')
            with patch.object(sync, 'ROOT', root), patch.object(sync.art, 'ASSETS', assets):
                profile = {'login': sync.OWNER, 'name': 'Zaw', 'bio': 'hi'}
                sync.generate(profile, [repo('project')])
                first = (root / 'README.md').read_text(encoding='utf-8')
                profile['bio'] = 'Enjoy learning'
                sync.generate(profile, [repo('project')])
                second = (root / 'README.md').read_text(encoding='utf-8')
                self.assertEqual(first, second)
                self.assertIn('https://example.com/api/banner?v=4', first)
                self.assertNotIn('Enjoy learning', second)


if __name__ == "__main__":
    unittest.main()
