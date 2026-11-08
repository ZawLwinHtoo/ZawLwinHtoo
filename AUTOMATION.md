# Automatic profile updates

Edit your name and bio using **Edit profile** on GitHub, then reload your profile.
The banner is a live SVG served by the `zaw-live-profile` Vercel project. Each
request reads your current public profile and renders the name, exact bio text,
and related illustration. It does not depend on GitHub Actions to detect bio
edits. Clearing the bio displays your name. Normal words remain intact when text
wraps. The source lives in `api/banner.py` and the renderer in `tools/`.

The endpoint sends `no-cache`, `no-store`, and `must-revalidate` headers. GitHub's
Camo image proxy and browser caching may still delay an image briefly; an already
open GitHub page cannot fetch a changed bio until the page/image is reloaded.
The prior committed introduction was removed so it cannot repeat an old bio.

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
All cards have project-specific artwork: route maps, restaurant menus, parking
bays, collaborative canvases, conveyor scanning, a code vault, education, linked
devices, browser layouts, or release pipelines. Colors follow each project.
Desktop uses one featured card plus two smaller cards; mobile uses three full
width cards so the text remains readable.

The workflow refreshes repository metadata on its schedule, after generator
changes, or manually under **Actions → Refresh profile → Run workflow**. GitHub
can delay or skip scheduled jobs. This affects newly added projects, not the
live bio. Changed static assets get content-hashed URLs. The carousel animates
independently of metadata checks.

The live image uses public profile HTML and requires no GitHub access token or
AI image service. The workflow uses its built-in token to commit static assets.
Vercel hosting is configured in `live-profile.json`, `vercel.json`, and
`pyproject.toml`. Redeploy the Vercel project after changing the live API or its
renderer modules. A Git push updates the README/assets but does not redeploy
the separately hosted image service automatically.
Metadata fetch failures fail the run and leave the published profile intact.
GitHub may disable scheduled workflows after 60 days without repository activity;
if that happens, enable the workflow again from the Actions tab.

To verify locally:

```sh
python -m unittest discover -s tools -p 'test_*.py'
python tools/update_profile.py
```

Hosted example renders (without changing your actual bio):

- `https://zaw-live-profile.vercel.app/api/banner?example=hello`
- `https://zaw-live-profile.vercel.app/api/banner?example=learning`

Add `&mobile=1` to preview the mobile layout. Without `example`, the endpoint
always reads your current public profile. Upstream failures return HTTP 503
instead of silently showing an old bio as current.

For an offline preview, use `--snapshot snapshot.json`
where the JSON contains `profile` (public user API object) and `repos` (all public
repository API objects). Keep snapshots local. Don't run the legacy
`generate_artwork.py` alone to refresh your profile: it regenerates the original
static artwork. Use `update_profile.py` for profile updates.
