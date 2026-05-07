# Submission Info

## Title

A Reproducible Versioned Event Graph Prototype for Evidence-Constrained Financial Event Stream Simulation

## Keywords

- event graph
- financial event stream
- evidence traceability
- discrete-event replay
- versioned graph

## Abstract

Financial event extraction systems often produce structured records, but downstream simulation and auditing workflows also require explicit evidence links, graph update histories, and reproducible replay artifacts. This paper presents a reproducible prototype for evidence-constrained financial event stream simulation. The prototype normalizes financial event records, checks exact evidence-span containment, applies a small set of graph update operators to a versioned event graph, and runs a discrete-event replay simulation over a controlled perturbation stream. In the current deterministic run, the prototype replays 70 records, produces 40 active events, writes 70 version logs, and marks 10 unresolved conflicts. The evaluation focuses on framework behavior rather than benchmark-level extraction comparison: schema validity, evidence coverage, update-operator agreement, replay completeness, and trace generation. The results show that the prototype can expose auditable graph transitions under controlled perturbations while keeping claims limited to the implemented reproducibility setting.
