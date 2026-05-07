# Stage 05 Server Run

cwd: /home/TJK/i3m_financial_event_graph_2026
python: Python 3.10.20

## run_demo
Processed records: 70
Active events: 40
Version logs: 70
Conflicts: 10
Wrote outputs to: /data/TJK/i3m/outputs

## run_ablation
Wrote ablation results: /data/TJK/i3m/tables/ablation_results.csv
Direct: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Schema: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Evidence: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Full: schema=1.000000 evidence=1.000000 merge=1.000000 conflict=1.000000 replay=1.000000

## build_case_study
Wrote case study: /data/TJK/i3m/tables/case_study_updates.csv (70 rows; operators=ADD_EVENT,MARK_CONFLICT,MERGE_EVENT,UPDATE_SLOT)

## plot_stage5_figures
Stage 05 figures renderer: stdlib_png
Read ablation rows: 4
Read case-study rows: 70
Read replay rows: 70
Wrote figures: paper/figures
Wrote tables: paper/tables

## generated file checks
OK /data/TJK/i3m/outputs/replay_trace.jsonl bytes=33415
OK /data/TJK/i3m/outputs/updates.jsonl bytes=18701
OK /data/TJK/i3m/outputs/conflicts.jsonl bytes=2840
OK /data/TJK/i3m/tables/ablation_results.csv bytes=335
OK /data/TJK/i3m/tables/case_study_updates.csv bytes=8920
OK paper/figures/fig1_framework.png bytes=16558
OK paper/figures/fig2_update_state_transition.png bytes=16292
OK paper/figures/fig3_case_study_replay_trace.png bytes=17159
OK paper/tables/table1_event_record_schema.md bytes=1260
OK paper/tables/table2_ablation_results.md bytes=470
OK paper/tables/table3_case_study_update_log.md bytes=10453

gpu_used: no
training: no
no_gpu_training_required
