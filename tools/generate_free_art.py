"""Generate one cached bio illustration, optionally saving proof examples."""
import argparse
import json
from pathlib import Path

from update_profile import ROOT, clean, render_banner
from free_visual import cached_visual, generate_visual, save_visual

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--examples', action='store_true')
args = parser.parse_args()
profile = json.loads((ROOT / '.profile-snapshot.json').read_text(encoding='utf-8'))['profile']
bio = clean(profile.get('bio')) or clean(profile.get('name')) or profile['login']
drawing = cached_visual(bio) or generate_visual(bio)
save_visual(bio, drawing)
if args.examples:
    for index, subject in enumerate(['apple', 'a dancing elephant']):
        visual = generate_visual(subject)
        example = {**profile, 'bio': subject}
        path = ROOT / f'assets/bio-proof-{index+1}.svg'
        path.write_text(render_banner(example, visual=visual), encoding='utf-8', newline='\n')
