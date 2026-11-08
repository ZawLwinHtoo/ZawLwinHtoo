# Automatic profile updates

Edit your name and bio using **Edit profile** on GitHub. The banner (desktop and
mobile), introduction, and banner alt text use that public data. Clearing your
bio uses your name in the banner. Long bios wrap and scale to fit.

The illustration follows common keywords: hi/hello gives a waving hand, bugs a
circuit beetle, code a terminal, AI a chip, web a globe, music musical notes,
nature a plant, gaming a controller, space a rocket, learning a book, and love
a heart. Other text gets geometric artwork with letters from the current bio.
This is keyword matching, not an AI image-generation service.

Selected builds is an SVG carousel that slides to another group of up to three
repositories every six seconds while the page is open. Every project participates,
including forks and archived repositories; only this profile repository itself
is excluded. New, renamed, deleted, and newly private repos are reflected on the
next successful refresh. Descriptions come from each repo's GitHub description.
The last slide wraps to the first projects as needed to fill three slots. Reduced
motion settings disable sliding and leave the first slide visible. GitHub displays
the carousel as an image, so individual cards cannot have changing clickable links.
The **Open a repository** section below it contains correct links for every project.
The original three illustrations are retained for their matching projects;
other repos get cards in the same charcoal, lime, orange, and blue palette.

The workflow checks metadata every five minutes (at minutes 2, 7, 12, and so on), after generator changes, or
manually under **Actions → Refresh profile → Run workflow**. GitHub schedules
can be delayed, and cached images may take additional time to refresh. Changes
are scheduled, not immediate when you save your GitHub bio. A page reload shows
the latest synced bio. Changed images get content-hashed URLs to avoid reusing
old image cache entries. The carousel animates independently of metadata checks.

No personal access token, external service, or paid dependency is needed. The
workflow reads public metadata and uses its built-in token to commit changes.
Metadata fetch failures fail the run and leave the published profile intact.
GitHub may disable scheduled workflows after 60 days without repository activity;
if that happens, enable the workflow again from the Actions tab.

To verify locally:

```sh
python -m unittest discover -s tools -p 'test_*.py'
python tools/update_profile.py
```

For an offline preview, use `--snapshot snapshot.json`
where the JSON contains `profile` (public user API object) and `repos` (all public
repository API objects). Keep snapshots local. Don't run the legacy
`generate_artwork.py` alone to refresh your profile: it regenerates the original
static artwork. Use `update_profile.py` for profile updates.
