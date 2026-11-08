# Free profile automation

Everything runs in `ZawLwinHtoo/ZawLwinHtoo` using standard GitHub-hosted Ubuntu
Actions runners. No paid API, payment method, separate hosting account,
Hugging Face account, or API key is required. Standard runners are free for
public repositories; no larger runner or billable model service is used.

## How bio updates work

1. Edit your name or bio in GitHub's **Edit profile** form.
2. The refresh workflow reads the public profile and compares the complete bio
   with the saved artwork metadata.
3. When it changes, a public Qwen model runs locally on the Actions CPU. It
   interprets the entire bio and chooses a main subject and supporting emoji.
4. Matching OpenMoji SVG illustrations are embedded into the banner. All files
   are committed to this repository, and the README uses content-hashed URLs.
5. Reload your profile to see the new banner.

The workflow checks approximately every five minutes. Scheduling can be delayed
by GitHub, and the first model download/inference adds some time. Changes are
not instantaneous. For a manual refresh, open **Actions → Refresh profile → Run
workflow**. An already open README image cannot observe a saved bio by itself.

## Open-ended text and visual limits

The complete bio is interpreted by a language model. It is not matched against
a hand-written list of words or three fixed examples. New words, sentences,
moods, and languages can be accepted, but model interpretations are not always
perfect. The final illustration uses the closest supported OpenMoji subjects;
it cannot depict every conceivable concept exactly or invent entirely new art.

The current OpenMoji library contains 4,567 icons. A main illustration plus a
supporting icon provides combinations for compound subjects. The original case
and spelling of the bio are preserved in the headline. Clearing the bio uses
the current GitHub name.

Artwork is cached in `assets/bio-art.json` and reused only for the same complete
bio and renderer version. A changed bio never reuses another bio's artwork.
The model download is needed only for a new interpretation. Large model weights
are temporary and are not committed or retained in an Actions cache/artifact.
If illustration generation fails, current bio text is still published and the
workflow reports the failure so it can be retried.

## Sources

- Model: `Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF`, Apache-2.0.
  https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF
- The exact model revision and SHA-256 are pinned in `tools/free_visual.py`.
- Runtime: `llama-cpp-python==0.3.36`, using its publisher's CPU wheels.
- Graphics: OpenMoji, CC BY-SA 4.0. See `assets/ART-LICENSE.md` for attribution.

## Project carousel

All public project repos take turns, three at a time, with a new slide every six
seconds. Forks and archived repos participate; only the profile repository is
excluded. Desktop uses one featured card plus two small cards. Mobile stacks
three full-width cards. Reduced-motion preferences disable sliding.

The image cannot give individual moving cards different clickable links on
GitHub. **Open a repository** below it contains the correct project links.

## Verification

```sh
python -m unittest discover -s tools -p 'test_*.py'
python tools/prepare_profile.py
python tools/update_profile.py --snapshot .profile-snapshot.json
```

To generate new artwork locally, install the CPU runtime and run
`python tools/generate_free_art.py`. It downloads about 1.1 GB of public model
weights into the ignored `.models` directory. The workflow does this on GitHub,
so your computer does not need to stay on.
