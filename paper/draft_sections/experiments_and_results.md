# Experiments and Results

## Experimental Setup

The experiment uses the controlled financial event stream generated for the prototype. The current local run processes 70 replay records and writes replay artifacts under `outputs/`, including event records, update logs, conflict logs, version logs, and `outputs/replay_trace.jsonl`.

The experiment is a deterministic prototype check rather than a financial event extraction benchmark. It uses the implemented schema checker, exact evidence-span matcher, rule-based graph update operators, and replay-state logger. No model training, GPU inference, external API call, or market forecasting component is used.

Figure 1 summarizes the overall pipeline from financial event samples to replay traces and version logs. Figure 2 summarizes the implemented graph update operators and the corresponding graph and simulation-state transitions. Figure 3 visualizes the case-study replay trace generated from the current replay artifacts.

## Metrics

The ablation table reports schema validity, evidence coverage, merge accuracy, conflict accuracy, replay completeness, runtime per record, and record count. `Direct`, `Schema`, and `Evidence` are component rows, so merge, conflict, and replay metrics are marked as `NA` when they are not applicable. `Full` runs the complete replay pipeline and reports graph-update and replay metrics against the controlled stream metadata.

Schema validity measures whether records pass the required event-record fields and ISO-date checks. Evidence coverage measures whether the evidence span appears in the source text. Merge accuracy and conflict accuracy compare predicted operators with the controlled stream's expected operators for duplicate and conflict perturbations. Replay completeness measures whether replay steps are applied and logged.

## Results

Table 1 lists the event-record schema used by the prototype. Table 2 reports the current ablation output generated from `tables/ablation_results.csv`. In this controlled run, all four rows contain 70 records. Schema validity and evidence coverage are `1.000000` for `Direct`, `Schema`, `Evidence`, and `Full`; the component rows keep non-applicable merge, conflict, and replay metrics as `NA`.

The `Full` row reports merge accuracy `1.000000`, conflict accuracy `1.000000`, and replay completeness `1.000000` on the controlled stream. These values describe agreement with the deterministic perturbation metadata in the current prototype run. They should not be interpreted as broad extraction accuracy, market forecasting ability, or real-world financial utility.

The results indicate that schema constraints improve structural validity, while evidence constraints improve traceability. The full prototype further supports duplicate merging, slot updating, conflict marking, and replay trace generation.

## Case Study

Table 3 converts `tables/case_study_updates.csv` into a compact update log. The current case study contains 70 replay rows with the operators `ADD_EVENT`, `MERGE_EVENT`, `UPDATE_SLOT`, and `MARK_CONFLICT`. The replay starts by adding evidence-backed event nodes, then records duplicate merges, slot updates, and unresolved conflict marks as they appear in the controlled stream.

Figure 3 uses the same case-study and replay artifacts to show how operation types appear over replay steps. The final replay trace contains 70 steps, 40 active events, 70 version logs, and 10 conflict marks. This case study demonstrates that the prototype can expose graph updates and state changes as auditable artifacts for the controlled stream.
