# Automatic profile updates

Edit your name or bio using **Edit profile** on GitHub. The banner (desktop and
mobile), introduction, and banner alt text are generated from that public data.
Clearing your bio removes the previous slogan and uses your name in the banner.
Long bios wrap and scale to fit. The circuit beetle artwork remains animated.

Selected builds shows up to three public project repositories. Every scheduled
refresh moves the selection forward by three. Every project participates,
including forks and archived repositories; only this profile repository itself
is excluded. New, renamed, deleted, and newly private repos are reflected on the
next successful refresh. Descriptions come from each repo's GitHub description.
The original three illustrations are retained for their matching projects;
other repos get cards in the same charcoal, lime, orange, and blue palette.

The workflow runs at minutes 17 and 47 each hour, after generator changes, or
manually under **Actions → Refresh profile → Run workflow**. GitHub schedules
can be delayed, and cached images may take additional time to refresh. Changes
are scheduled, not immediate when you save your GitHub bio. Card links always
point to the project pictured. A page reload shows the latest saved selection.

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

For an offline preview, use `--snapshot snapshot.json --at 2026-11-09T12:00:00Z`
where the JSON contains `profile` (public user API object) and `repos` (all public
repository API objects). Keep snapshots local. Don't run the legacy
`generate_artwork.py` alone to refresh your profile: it regenerates the original
static artwork. Use `update_profile.py` for profile updates.
