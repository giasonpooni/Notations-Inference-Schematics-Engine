# Notations Inference Schematics Engine (NISE)

**Constructs query-specific inference graphs connecting physical systems, observations, models, constraints, uncertainty, and scientific instruments.**

NISE is a Notation Systems Inc instrument for building **candidate investigation structure**. It answers:

> What parts of the system, evidence, models, constraints and computational machinery are relevant to investigating this question?

It does **not** establish physical truth, estimate system state, execute scientific providers, admit evidence, or authorize actuation.

The central object is an inference schematic

```text
S_q = (V_q, E_q, M_q, C_q, O_q, P_q)
```

where:

- `V_q` — relevant entities, geometry and state variables;
- `E_q` — typed physical, causal and relational edges;
- `M_q` — candidate models;
- `C_q` — constraints and assumptions;
- `O_q` — observations/evidence;
- `P_q` — applicable semantic computational operations.

Every retained relation has an epistemic status such as `OBSERVED`, `DERIVED`, `DECLARED`, or `HYPOTHESIZED`.

Intended flow:

```text
question
   ↓
NISE
   ↓
candidate inference schematic
   ↓
NET semantic capabilities / specialist instruments
   ↓
retained executions and results
```

FrameMapper owns representation of known state. State-estimation instruments own state inference. NET owns execution/composition. NISE owns candidate investigation structure.

This repository is newly initialized; implementation work proceeds on reviewable branches.

## Organization

**Notation Systems Inc** is the parent organization: a scientific computing and systems engineering company developing computational instruments, software and interactive environments for understanding and building physical and virtual systems.

The company's development direction connects measurement, state estimation and sensor fusion, scientific modelling, simulation and execution, from materials and machines to interactive worlds.

| Division | Focus |
| --- | --- |
| **Notations Gaming** | Games, graphics, world building, interactive environments and gameplay simulation. |
| **Notations Manufacturing** | Design, machinery integration, process development, fabrication and production systems. |
| **Notations Laboratories** | Research and experimental validation in scientific computing, measurement, physics and chemistry modelling, materials and simulation. |

**Repository role:** This repository documents NISE's shared **Notation Systems Inc** role in constructing candidate investigations connecting systems, observations, models, constraints and instruments. It supports the company's broader physical and virtual systems direction while NET retains session composition, execution and distinct evidence, operation, execution and verification identities.

## Instrument role

[Notations Systems Terminal](https://github.com/atomtrapping/Notations-Systems-Terminal) owns composition and execution history. FrameMapper owns supported representations; estimation instruments infer state under their own models; ESM retains governed evidence admission. Notations Gaming develops interactive worlds, simulation technology and digital IP with separate creative state and review.

[Current organization](#organization) · [Historical research protocol](https://github.com/atomtrapping/Notations-Systems-Terminal/blob/b41b84922d4963a9206202029afd1e78b9451f9c/RESEARCH_PROGRAMME.md)

## Research profile

**Question:** what structure is sufficient for a declared task, and what does reduction omit?

Compare full and reduced contexts on fixed tasks, including counterexamples with hidden coupling, contradictory sources, missing calibration and budget exclusions. Measure selection/reduction overhead, retained dependencies, task fidelity, context size and total human effort. A small graph is useful only if it preserves what the task needs.

Exact minimum, minimal-by-ablation, heuristic reduction and approximate sufficiency are different claims. A graph slice is not automatically a closed dynamical system; external forcing, correlations and boundary conditions may still matter. General semantic retrieval, information-optimal planning and mathematical sufficiency guarantees remain research goals.
