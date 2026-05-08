# Public Mini-Case Source Manifest

- dataset name: FewFC
- upstream repository: `https://github.com/TimeBurningFish/FewFC`
- local source path used: `data/raw/FewFC`
- local upstream commit observed: `ec6cac90238c04b45d4512a695ee6375fc72af2f`
- license note observed: FewFC public research dataset; CC BY-SA 4.0; see upstream repository
- converted records: 20
- committed mini-case path: `data/samples/public_mini_events.jsonl`
- source URL recorded in samples: `https://github.com/TimeBurningFish/FewFC`

The full raw FewFC dataset is not committed because it is an upstream public dataset and should remain under its original repository, provenance, and license terms. The repository commits only a lightweight converted sanity sample with explicit source metadata and license notes.

The mini-case is not an extraction benchmark. It does not report extraction F1, compare extraction systems, or expand the paper into a full FewFC/DuEE-Fin/DocFEE benchmark. It only checks whether a small set of public financial event records can pass the same schema, evidence-span containment, and replay path used by the controlled-replay prototype.

Exact regeneration command after downloading FewFC:

```bash
python scripts/prepare_public_mini_case.py --source fewfc --input-dir data/raw/FewFC --out data/samples/public_mini_events.jsonl --max-records 20 --seed 42
```

If FewFC is unavailable or unparsable, do not fabricate replacement records.
