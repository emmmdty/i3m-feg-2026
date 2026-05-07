# Stage 6.7 Validation

## Acceptance commands

Preflight:

```bash
pwd
git branch --show-current
git status
```

Local reproduction:

```bash
python scripts/build_seed_financial_samples.py --out data/samples/seed_financial_events.jsonl --n 30 --seed 42
python scripts/generate_perturbation_stream.py --input data/samples/seed_financial_events.jsonl --out data/processed/controlled_stream.jsonl --seed 42 --duplicates 10 --conflicts 10 --updates 10 --shuffle
python scripts/run_demo.py
python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv
python scripts/run_metadata_hidden_replay.py --input data/processed/controlled_stream.jsonl --out tables/metadata_hidden_results.csv --tex-table paper/i3m_submission/tables/table_metadata_hidden.tex
bash paper/i3m_submission/build_latex.sh
pdfinfo paper/manuscript_i3m2026_v2.pdf
pdftotext paper/manuscript_i3m2026_v2.pdf reports/stage_06_7/manuscript_i3m2026_v2_validation.txt
```

## Author and claim checks

- `manuscript.tex` and PDF text contain Jiakai Tong, Yue Zhao, Harbin Institute of Technology, School of Astronautics, and `emmmtjk@163.com`.
- Placeholder author and affiliation text is absent from `manuscript.tex` and PDF text.
- The title is `A Controlled-Replay Prototype for Auditable Versioned Financial Event Graph Updates`.
- The manuscript explicitly frames the work as a controlled-replay prototype on synthetic controlled streams.
- The manuscript states that it does not evaluate financial event extraction accuracy or market prediction.
- The manuscript limits claims to the implemented prototype and rejects benchmark-level generalization.
- The manuscript states that replay agreement metrics are controlled-label agreement and not general extraction or deployment accuracy.
- Restricted overclaim and finance-action phrase scan returned no matches in `manuscript.tex` or PDF text.

## Metadata-hidden check

- `tables/metadata_hidden_results.csv` and `paper/i3m_submission/tables/table_metadata_hidden.tex` contain `Full-control` and `Metadata-hidden`.
- The table exposes metadata yes/no, Merge, Conflict, Update, Operator, Replay, and Runtime fields.
- Local rerun summary:
  - Full-control: metadata=yes, merge=1.000000, conflict=1.000000, update=1.000000, operator=1.000000, replay=1.000000, runtime=0.015998 ms/record.
  - Metadata-hidden: metadata=no, merge=0.200000, conflict=0.800000, update=0.700000, operator=0.585714, replay=1.000000, runtime=0.011688 ms/record.
- Code inspection confirms `strip_replay_metadata()` removes `perturbation_type`, `expected_operator`, `base_event_id`, and `gold_group_id` before `simulate_replay()`.
- Dynamic leak check over 70 stripped records found `metadata_leaks=[]`.
- `expected_operator` is read from gold records only inside post-hoc `operator_agreement()`.

## PDF check

- `paper/manuscript_i3m2026_v2.pdf` exists.
- `pdfinfo` reports `Creator: LaTeX with hyperref`, `Producer: pdfTeX-1.40.22`, and `Pages: 7`.
- PDF text contains no placeholder text and no stage-label leakage.
- PDF text contains no restricted overclaim or finance-action phrases.
- Rendered page checks for the dense figure/table pages show no obvious figure or table overflow.
- `paper/i3m_submission/manuscript.tex` references `\input{tables/table_metadata_hidden.tex}`, and the PDF text includes Table 3 `Metadata-hidden diagnostic replay agreement`.

## Server reproduction check

`reports/stage_06_7/stage_06_7_report.md` records server reproduction from `/home/TJK/i3m_financial_event_graph_2026` using `/home/TJK/.conda/envs/tjk-feg/bin/python`.

- `scripts/run_demo.py` succeeded on the server with outputs under `/data/TJK/i3m/outputs`.
- `scripts/run_ablation.py` succeeded on the server with output `/data/TJK/i3m/tables/ablation_results.csv`.
- `scripts/run_metadata_hidden_replay.py` succeeded on the server with output `/data/TJK/i3m/tables/metadata_hidden_results.csv`.
- Server report records `training: no`, `model inference: no`, `external API calls: none`, and `no_gpu_training_required`.

## Decision

PASS.

Stage 6.7 acceptance passed. Stage 7 submission-package work is allowed after Git closeout remains clean.

Accepted patch commit before validation rerun: `7902f953d706b723564d5817ee3b2d4fc29a99b2`.

Validation commit hash: `b12f6c38634a23e6daade1e116adc421eed6feb7`.
