# Notations Inference Schematics Engine (NISE)

**Constructs query-specific inference graphs connecting physical systems, observations, models, constraints, uncertainty, and scientific instruments.**

NISE is a Notation Systems instrument for building **candidate investigation structure**. It answers:

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
