"""Read public metadata and decide whether a new local-model run is needed."""
import json
import os

from update_profile import ROOT, OWNER, clean, fetch_metadata
from free_visual import cached_visual

profile, repos = fetch_metadata(OWNER)
(ROOT / '.profile-snapshot.json').write_text(json.dumps({'profile': profile, 'repos': repos}), encoding='utf-8')
bio = clean(profile.get('bio')) or clean(profile.get('name')) or profile['login']
needs_art = cached_visual(bio) is None
print('New artwork needed:', needs_art)
if os.environ.get('GITHUB_OUTPUT'):
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write(f'needs_art={str(needs_art).lower()}\n')
