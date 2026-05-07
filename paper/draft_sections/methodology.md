# Methodology

## Evidence-Constrained Event Records

Each input item is treated as an event record with both event-level fields and source-level evidence. The required event fields are `event_id`, `event_type`, `subject`, `object`, `time`, `trigger`, `evidence_span`, and `source_doc_id`. Stream records may store the event payload under an `event` object while keeping replay metadata at the top level. The schema module normalizes both forms into a flat event record before validation.

An event record is accepted by the evidence module only when its `evidence_span` is a non-empty string and appears in the corresponding `source_text`. This is an exact-span check. It does not infer missing evidence and does not use a learned verifier. In the replay pipeline, schema validation and evidence matching are gate checks before any graph update is applied.

## Versioned Event Graph

At replay step `t`, the prototype maintains a versioned event graph:

`G_t = (V_t, E_t, L_t)`

Here, `V_t` contains active event nodes and entity nodes, `E_t` contains event-entity edges, and `L_t` contains append-only version logs. The graph is stored in memory using dictionaries for event and entity nodes and lists for edges, version logs, conflicts, and merge records.

Each accepted stream record induces a transition:

`G_t -> G_{t+1}`

The transition either inserts an event node, merges an incoming duplicate into an existing event, updates slots of a target event, marks a conflict, or appends a version log. The graph version is the length of `L_t`, so every applied operator creates an auditable log entry.

## Graph Update Operators

The prototype uses only five operators:

- `ADD_EVENT`
- `MERGE_EVENT`
- `UPDATE_SLOT`
- `MARK_CONFLICT`
- `VERSION_LOG`

`ADD_EVENT` inserts an event node, upserts subject and object entity nodes, and appends event-entity edges. `MERGE_EVENT` records that an incoming duplicate refers to a target event without creating a new active event node. `UPDATE_SLOT` records changed slots for a target event and updates the stored event fields. `MARK_CONFLICT` creates an unresolved conflict mark with the incoming event, target event, and source metadata. `VERSION_LOG` appends the operator history for every graph transition.

The operator set is intentionally small. It is sufficient for the current controlled stream because the stream contains base records, duplicates, slot updates, conflicts, and temporal replay records. The methodology does not add a reversal operator beyond the five operators listed above.

## Discrete-Event Replay Simulation

Replay orders stream records by `arrival_index` when available, with the original file order as a fallback. For each ordered record, the simulator performs schema validation, evidence matching, rule-based operator prediction, target-event selection, graph update execution, and replay-state logging.

The simulation state transition is:

`S_t -> S_{t+1}`

The state vector written to the replay trace contains exactly these indicators:

- `graph_version`
- `active_event_count`
- `active_entity_count`
- `merged_event_count`
- `updated_slot_count`
- `conflict_count`
- `unresolved_conflict_count`
- `replay_step`

These indicators are descriptive replay diagnostics. They are not financial forecasts and are not used to rank market outcomes. Their role is to make each graph transition observable and reproducible.

## Consistency Checking Modules

The prototype uses rule-based consistency checking modules. The schema checker verifies required fields and ISO date format. The evidence checker verifies exact evidence-span containment in the source text. The conflict module predicts an update operator using perturbation metadata when present and simple event-level rules otherwise. Target selection first uses `base_event_id` when it refers to an active graph event, then falls back to matching event type, subject, time proximity, amount, and status.

Duplicate checks compare subject, event type, time proximity, amount, and status. Update checks require an update signal and changed fields. Conflict checks require the same subject and event type, close event time, and a difference in amount or status supported by conflict-like source text or status changes. These modules are deterministic and are designed to expose the prototype behavior rather than to estimate real-world event probabilities.

## Controlled Perturbation Stream

The controlled perturbation stream starts from deterministic financial event samples and adds four perturbation families: duplicates, conflicts, updates, and temporal replay records. Each perturbation includes an `expected_operator` field so that replay behavior can be checked against the intended transition type.

In the current controlled run, the seed sample file contains 30 financial event samples. The generated stream contains 70 records: base records, duplicate records, conflict records, update records, and temporal replay records. The replay artifacts therefore provide a compact testbed for checking schema constraints, evidence constraints, graph update operators, and replay-state logging under deterministic inputs.
