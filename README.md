# A Controlled-Replay Prototype for Auditable Versioned Financial Event Graph Updates

This repository contains the reproducible artifact for an I3M/EMSS 2026 submission on evidence-gated replay for versioned financial event graph updates.

## Scope

The artifact studies controlled replay, version logs, target-resolution checks, metadata-hidden diagnostics, negative controls, invariant checks, a small FewFC-derived mini-case, and a lightweight scale sanity run. It is not an event extraction benchmark and does not evaluate market forecasting.

## Reproduction

Run from the repository root:

```bash
bash scripts/reproduce_all.sh
```

The command regenerates deterministic sample data, replay traces, diagnostic CSVs, LaTeX tables, vector figures, and the final PDF.

## Final PDF

- `paper/i3m_submission/manuscript.pdf`
- `paper/manuscript_i3m2026_v2.pdf`

## Data Notes

- `data/samples/seed_financial_events.jsonl` contains deterministic synthetic records used to build the controlled replay stream.
- `data/samples/public_mini_events.jsonl` contains 20 FewFC-derived records used only as an external sanity check.
- Raw upstream data and generated replay outputs are not committed.

## License

Code and artifact files are released under the MIT License in `LICENSE`.

## Citation

Please cite the accompanying I3M/EMSS 2026 paper if you use this artifact.
