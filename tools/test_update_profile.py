from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import update_profile as sync


def repo(name, **extra):
    return {"name": name, "owner": {"login": sync.OWNER}, "private": False,
            "language": "Python", "description": None, **extra}


class ProfileTests(unittest.TestCase):
    def test_rotation_covers_every_project_without_duplicate_cards(self):
        now = datetime(2026, 11, 9, tzinfo=timezone.utc)
        for count in range(1, 35):
            repos = [repo(f"project-{i}") for i in range(count)]
            seen = set()
            for tick in range(count):
                selection = sync.select_projects(repos, now + timedelta(minutes=30 * tick))
                names = [r["name"] for r in selection]
                self.assertEqual(len(set(names)), min(3, count))
                seen.update(names)
            self.assertEqual(seen, {r["name"] for r in repos})
        self.assertEqual(sync.select_projects([], now), [])

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
        now = datetime(2026, 11, 9, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            assets = root / "assets"
            assets.mkdir()
            (root / "README.md").write_text((source / "README.md").read_text(encoding="utf-8"), encoding="utf-8")
            profile = {"login": sync.OWNER, "name": 'Zaw <&> "Htoo"', "bio": 'Build <things> & learn "daily"!'}
            projects = [repo("a-project", description="A <tool> & more"), repo("b-project"), repo("c-project")]
            with patch.object(sync, "ROOT", root), patch.object(sync.art, "ASSETS", assets):
                sync.generate(profile, projects, now)
                first = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                sync.generate(profile, projects, now)
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
                sync.generate(profile, [], now)
                self.assertNotIn("daily", (root / "README.md").read_text(encoding="utf-8"))
                self.assertNotIn("BUGS", (assets / "profile-banner.svg").read_text(encoding="utf-8"))

    def test_long_unicode_bio_fits_without_losing_text(self):
        for value in ["W" * 160, "Build useful things & learn every day. " * 4,
                      "မြန်မာစာ စမ်းသပ်ခြင်း " * 7, "こんにちは世界 " * 15]:
            lines, size = sync.fit_lines(value, 540, 190, largest=112)
            self.assertLessEqual(len(lines) * size * 1.06, 190)
            self.assertEqual("".join(lines).replace(" ", ""), sync.clean(value).replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
