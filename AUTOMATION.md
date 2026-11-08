# Automatic profile updates

## Open-ended AI artwork (awaiting account activation)

`api/ai-banner.py` is the new AI-powered image endpoint. It sends the complete
current bio to `google/gemini-3.1-flash-lite` through Vercel AI Gateway, rather
than choosing from a list of topics. A noun, phrase, non-English text, or invented
word can receive an original vector illustration. Interpretations are generated
by a model and cannot be guaranteed perfect for every possible string.

The renderer preserves the bio text, validates generated geometry, and rejects
scripts, external resources, event attributes, unsupported elements, and unsafe
paint values. It shares a bounded cache of artwork by the complete bio inside
each warm function instance. This cache is ephemeral; cold instances may make
another generation request. AI requests consume Gateway credits.

Activation is currently blocked. A real authenticated request returned HTTP 403
with `customer_verification_required`: the connected Vercel team must add a valid
payment method before Gateway will serve AI requests. No card, billing plan, or
credit purchase has been configured by the agent. Verify the account at
`https://vercel.com/sterix-z/~/ai`, then run a successful image request before
changing `live-profile.json` to the AI endpoint. The existing profile endpoint
continues serving the previous behavior until that switch is verified.

Vercel supplies the current invocation's OIDC token in `x-vercel-oidc-token`.
No token is committed or returned in responses. Missing credits or authentication
produce HTTP 503 with an explicit service error; this endpoint never silently
substitutes the preset picker and calls that AI generation.

## Current published endpoint

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
