# Stage 6.7 Short-Paper Rescue Patch Report

## 1. Why Stage 6.7 was inserted

Stage 6.7 was inserted after Stage 6.5 and Stage 6.6 because expert review identified remaining short-paper submission risks in the compiled I3M/EMSS LaTeX version. The rescue patch narrows the paper to a controlled-replay prototype and auditability case study.

## 2. Expert-review issues addressed

- Author and affiliation metadata still used placeholders.
- The title and abstract claimed too much generality.
- The Full row's `1.000000` values were driven by controlled metadata.
- `predict_operator` prioritizes `perturbation_type`, so operator values cannot be described as general model accuracy.
- Paper-facing metrics needed to be agreement under injected perturbations.
- A metadata-hidden replay diagnostic was needed.
- The positioning needed to be EMSS/I3M short paper, reproducible controlled-replay prototype, and auditability case study.

## 3. Author metadata replacement

- Author: Jiakai Tong.
- Corresponding author: Yue Zhao.
- Affiliation: School of Astronautics, Harbin Institute of Technology, Harbin, China.
- Email: `emmmtjk@163.com`.
- Removed LaTeX placeholder author/affiliation text from the current submission manuscript.

## 4. Title claim reduction

The submission title is now:

`A Controlled-Replay Prototype for Auditable Versioned Financial Event Graph Updates`

The same title is reflected in the LaTeX manuscript, compiled PDF metadata, and submission info.

## 5. Accuracy-to-agreement change

Paper-facing metric labels and table captions now use controlled replay agreement language. The paper explicitly states that agreement metrics compare replay decisions with injected perturbation labels under controlled conditions and should not be interpreted as general extraction or deployment accuracy.

The legacy CSV fields `merge_accuracy` and `conflict_accuracy` remain for backward compatibility in existing scripts.

## 6. Metadata-hidden experiment design

The new script `scripts/run_metadata_hidden_replay.py` compares:

- `Full-control`: original controlled stream records, including perturbation metadata.
- `Metadata-hidden`: records stripped before decision logic of `perturbation_type`, `expected_operator`, `base_event_id`, and `gold_group_id`.

The hidden setting keeps only event fields for replay decisions. Gold `expected_operator` labels are used only after replay for agreement scoring.

## 7. Metadata-hidden experiment results

Local `tables/metadata_hidden_results.csv`:

| setting | metadata | records | merge | conflict | update | operator | replay | ms/record |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full-control | yes | 70 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.019718 |
| Metadata-hidden | no | 70 | 0.200000 | 0.800000 | 0.700000 | 0.585714 | 1.000000 | 0.011532 |

This supports the paper's conservative interpretation: controlled metadata helps the current prototype, and metadata-hidden replay is a diagnostic check rather than a benchmark evaluation.

## 8. Public mini case

No public mini case was added in Stage 6.7. A public announcement mini-case is left for the camera-ready extension. No public data was fabricated.

## 9. Local commands and results

Executed locally:

```bash
python scripts/build_seed_financial_samples.py --out data/samples/seed_financial_events.jsonl --n 30 --seed 42
python scripts/generate_perturbation_stream.py --input data/samples/seed_financial_events.jsonl --out data/processed/controlled_stream.jsonl --seed 42 --duplicates 10 --conflicts 10 --updates 10 --shuffle
python scripts/run_demo.py
python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv
python scripts/build_case_study.py --replay outputs/replay_trace.jsonl --updates outputs/updates.jsonl --conflicts outputs/conflicts.jsonl --out tables/case_study_updates.csv
python scripts/generate_negative_controls.py --input data/samples/seed_financial_events.jsonl --out data/processed/negative_control_stream.jsonl --seed 42
python scripts/run_sanity_checks.py --input data/processed/negative_control_stream.jsonl --out tables/sanity_check_results.csv --tex-table paper/i3m_submission/tables/table_negative_controls.tex
python scripts/run_scale_sensitivity.py --out tables/scale_sensitivity_results.csv --figure paper/i3m_submission/figures/fig_runtime_scaling.pdf --tex-table paper/i3m_submission/tables/table_scale_sensitivity.tex --seed 42 --scales 30 60 120 240
python scripts/run_metadata_hidden_replay.py --input data/processed/controlled_stream.jsonl --out tables/metadata_hidden_results.csv --tex-table paper/i3m_submission/tables/table_metadata_hidden.tex
python scripts/make_submission_tables.py --ablation tables/ablation_results.csv --case-study tables/case_study_updates.csv --sanity tables/sanity_check_results.csv --scale tables/scale_sensitivity_results.csv --metadata-hidden tables/metadata_hidden_results.csv --out-dir paper/i3m_submission/tables
bash paper/i3m_submission/build_latex.sh
```

Key local results:

- Controlled stream: 70 records.
- Demo replay: 40 active events, 70 version logs, 10 conflicts.
- Full replay row: merge agreement `1.000000`, conflict agreement `1.000000`, replay completeness `1.000000`.
- Negative controls: 20 cases, 10 schema rejected, 5 evidence rejected, 5 invalid dates rejected, 5 unknown operators handled, 0 crashes.
- Scale sensitivity:
  - 30 seed scale: 70 replay records, 0.013789 ms/record.
  - 60 seed scale: 140 replay records, 0.012894 ms/record.
  - 120 seed scale: 280 replay records, 0.015027 ms/record.
  - 240 seed scale: 560 replay records, 0.017334 ms/record.

## 10. Server reproduction commands and results

Code was synchronized to:

`gpu-4090:/home/TJK/i3m_financial_event_graph_2026/`

without `--delete`.

Executed on the server from `/home/TJK/i3m_financial_event_graph_2026` using `/home/TJK/.conda/envs/tjk-feg/bin/python`:

```bash
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/build_seed_financial_samples.py --out data/samples/seed_financial_events.jsonl --n 30 --seed 42
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/generate_perturbation_stream.py --input data/samples/seed_financial_events.jsonl --out data/processed/controlled_stream.jsonl --seed 42 --duplicates 10 --conflicts 10 --updates 10 --shuffle
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_demo.py --outputs-dir /data/TJK/i3m/outputs
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_ablation.py --config configs/stage3_experiment.json --out /data/TJK/i3m/tables/ablation_results.csv
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_metadata_hidden_replay.py --input data/processed/controlled_stream.jsonl --out /data/TJK/i3m/tables/metadata_hidden_results.csv --tex-table /data/TJK/i3m/reports/stage_06_7/table_metadata_hidden.tex
```

Server key results:

- Demo replay: 70 records, 40 active events, 70 version logs, 10 conflicts.
- Full replay row: merge agreement `1.000000`, conflict agreement `1.000000`, replay completeness `1.000000`.
- Metadata-hidden row: merge `0.200000`, conflict `0.800000`, update `0.700000`, operator `0.585714`, replay `1.000000`.
- Server small report synced to `reports/stage_06_7/server_data_reports/`.

## 11. Training status

training: no

## 12. GPU status

no_gpu_training_required

## 13. Model/API status

- model inference: no
- external API calls: none

## 14. PDF rebuild status

`bash paper/i3m_submission/build_latex.sh` completed successfully and wrote:

- `paper/i3m_submission/manuscript.pdf`
- `paper/manuscript_i3m2026_v2.pdf`

## 15. PDF page count

`pdfinfo paper/manuscript_i3m2026_v2.pdf` reports:

- Pages: 7

## 16. Risk-word check

`pdftotext` output was written to:

`reports/stage_06_7/manuscript_i3m2026_v2.txt`

Forbidden PDF-text checks returned no matches for:

`TBD`, `Stage 06`, `Stage 6`, `GPT-generated`, `Codex-generated`, `AI-generated`, `stock prediction`, `trading signal`, `buy recommendation`, `sell recommendation`, `investment advice`, `outperform`, `state-of-the-art method`, `superior performance`, `Instructions to Authors`, `Insert here your abstract text`.

Expected terms are present in the PDF text:

- agreement
- controlled replay
- synthetic controlled stream
- short paper
- prototype

## 17. Recommendation

Stage 6.7 is ready for user acceptance review. The paper is now framed as a controlled-replay prototype and auditability case study, with metadata-hidden replay results included and interpreted conservatively.

## 18. Git status

This stage has not been committed. Git submission is intentionally deferred for user acceptance.
