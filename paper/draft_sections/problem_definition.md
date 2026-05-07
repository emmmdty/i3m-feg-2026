# Problem Definition

This prototype studies evidence-constrained financial event stream simulation. The task is not to build a financial event extraction benchmark winner. Instead, it defines a reproducible setting in which event records are checked, inserted into a versioned graph, updated by a small operator set, and replayed as a discrete event stream.

## Inputs

The input consists of two related streams.

First, the prototype uses financial event samples. Each sample contains an event identifier, event type, subject, object, event time, trigger, evidence span, source document identifier, source text, amount, and status. In the current implementation, these samples are stored as deterministic JSONL records under `data/samples/seed_financial_events.jsonl`.

Second, the prototype uses a controlled perturbation stream. The stream wraps event payloads with metadata such as `stream_record_id`, `base_event_id`, `gold_group_id`, `arrival_index`, `perturbation_type`, `expected_operator`, `source_doc_id`, and `source_text`. The controlled stream contains base records and deterministic perturbations for duplicate, conflict, update, and temporal replay cases. This stream is generated under `data/processed/controlled_stream.jsonl`.

## Outputs

The output is a set of replay artifacts that expose both the graph state and the update history.

- A versioned event graph stores active event nodes, entity nodes, event-entity edges, and graph-version logs.
- Version logs record the operator applied at each replay step and the target event when applicable.
- Conflict marks store unresolved conflict records produced by rule-based conflict checks.
- Replay traces record the step-by-step transition history for the controlled stream.
- Simulation state indicators summarize the graph after each replay step, including counts for active events, active entities, merges, updates, conflicts, unresolved conflicts, graph version, and replay step.

## Research Questions

**RQ1: schema constraints.** How can a lightweight schema constraint module normalize flat event records and nested stream records while rejecting structurally invalid event inputs?

**RQ2: evidence constraints.** How can event records be constrained by explicit evidence spans so that graph updates are tied to text present in the source record?

**RQ3: update operators.** Can a small rule-based operator set express the required graph transitions for base events, duplicates, slot updates, conflicts, and version logging?

**RQ4: replay simulation.** Can the controlled perturbation stream be replayed into a versioned event graph while producing deterministic trace artifacts and simulation state indicators?
