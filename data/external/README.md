# External Public Dataset Staging

This directory is for lightweight pointers or locally staged public dataset
copies used by small reproducibility checks.

Stage 6.8 uses FewFC when available. The preferred local source is:

- `data/raw/FewFC`
- upstream: `https://github.com/TimeBurningFish/FewFC`
- license note: CC BY-SA 4.0, as documented by the upstream repository

Do not commit full external datasets, raw archives, model files, or generated
large outputs. The only public mini-case data intended for version control is
the small converted sample at `data/samples/public_mini_events.jsonl`.
