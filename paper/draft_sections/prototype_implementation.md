# Prototype Implementation

The prototype is implemented as a lightweight Python package and a small set of command-line scripts. The implementation is rule-based and uses local JSONL and CSV artifacts for reproducibility.

## Core Modules

`src/schema.py` defines event normalization and schema validation. It accepts both flat sample records and controlled stream records whose event payload is nested under `event`. The validator checks required event fields and verifies that `time` is an ISO date string.

`src/evidence.py` implements the evidence constraint. The main check returns true only when a non-empty `evidence_span` appears in `source_text`. This module provides the evidence gate used by the replay simulator and the evidence-coverage metric.

`src/graph_store.py` implements the in-memory versioned event graph. It stores event nodes, entity nodes, event-entity edges, version logs, conflict marks, merge records, and the update-slot counter. Its public graph update methods are `add_event`, `merge_event`, `update_slot`, `mark_conflict`, `append_version_log`, and `snapshot_state`.

`src/conflict.py` contains deterministic operator prediction and target-event selection rules. It maps controlled perturbation metadata to `MERGE_EVENT`, `MARK_CONFLICT`, `UPDATE_SLOT`, or `ADD_EVENT` when available, and otherwise falls back to event matching rules for duplicates, updates, and conflicts.

`src/simulator.py` runs the discrete-event replay. It orders records by `arrival_index`, applies schema and evidence gates, predicts the graph operator, executes the graph update, and writes replay trace entries with simulation state indicators.

`src/metrics.py` builds the ablation rows used in the experiment table. `Direct`, `Schema`, and `Evidence` are component rows with non-applicable merge, conflict, and replay metrics recorded as `NA`. `Full` runs the complete replay and reports schema validity, evidence coverage, merge accuracy, conflict accuracy, replay completeness, runtime per record, and record count.

## Reproduction Scripts

`scripts/run_demo.py` is the one-command replay entry point. It ensures the controlled stream exists, reads the stream, runs the full replay with schema and evidence gates enabled, and writes:

- `outputs/events.jsonl`
- `outputs/updates.jsonl`
- `outputs/version_logs.jsonl`
- `outputs/conflicts.jsonl`
- `outputs/replay_trace.jsonl`

`scripts/run_ablation.py` is the ablation entry point. It reads `configs/stage3_experiment.json` when provided, loads the controlled stream, builds the four ablation rows, and writes a CSV table.

The intended local reproduction commands are:

```bash
python scripts/run_demo.py
python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv
```

The Stage 03 summary path also uses `scripts/build_case_study.py` to convert replay updates and conflicts into a compact case-study CSV, and `scripts/summarize_experiment.py` to summarize ablation, case-study, and replay artifacts. These scripts do not start training or call external services.

## Current Reproducible Outputs

On the current controlled stream, `scripts/run_demo.py` processes 70 records and writes 40 active events, 70 version logs, and 10 conflict marks. The replay trace contains one row per replay step and includes the simulation state indicators described in the methodology draft.

The ablation output contains four rows: `Direct`, `Schema`, `Evidence`, and `Full`. In the current controlled run, schema validity and evidence coverage are `1.000000` for all rows. The merge, conflict, and replay metrics are `NA` for the component rows and `1.000000` for the `Full` row. These numbers describe deterministic agreement with the controlled perturbation stream and should not be interpreted as broad extraction accuracy claims.
