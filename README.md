# Notations Inference Schematics Engine (NISE)

**Constructs query-specific computational schematics linking evidence, entities, geometry, models, constraints, state variables, uncertainty, and available instruments for physical-system investigation.**

NISE answers:

> **What parts of the system, evidence, models and computational machinery are relevant to investigating this question?**

It does **not** answer:

> What is physically true?

The central object is an **Inference Schematic**:

```text
S_q = (V_q, E_q, M_q, C_q, O_q, P_q)
```

where:

- **V_q** — relevant entities, geometry and state variables;
- **E_q** — physical, causal and relational edges;
- **M_q** — candidate models;
- **C_q** — constraints and assumptions;
- **O_q** — observations/evidence;
- **P_q** — applicable semantic computational operations.

Edges and nodes retain one of:

`OBSERVED · DERIVED · DECLARED · HYPOTHESIZED`.

These are epistemic provenance labels, not confidence percentages.

## V1

The first implementation is deliberately bounded and deterministic.

```text
explicit query contract
        ↓
focus identities + requested capabilities
        ↓
bounded graph traversal
        ↓
hypothesis policy + node/hop budget
        ↓
candidate inference schematic
        ↓
NET / specialist instruments (separate authority)
```

**Natural-language question text is retained but does not secretly select nodes in V1.** This keeps the first engine falsifiable and prevents generic retrieval from masquerading as physical inference.

### Quickstart

```sh
python -m pip install -e '.[dev]'
nise compile examples/bearing_catalog.json examples/bearing_query.json \
  --output schematic.json
nise inspect schematic.json
python -m pytest
```

The included bearing example is synthetic and demonstrates:

- a physical entity and vibration state variable;
- one observed accelerometer record;
- a declared wear model and operating constraint;
- requested spectrum/state-estimation capabilities;
- one hypothesized damage relation withheld unless the query explicitly opts in;
- an unresolved fault-classification capability retained as a gap rather than fabricated.

## Boundary with adjacent systems

| Component | Question it owns |
|---|---|
| **NISE** | What evidence/system/model/instrument structure is relevant to this investigation? |
| **FrameMapper** | How should known state be represented spatially, temporally and relationally? |
| **State Estimator** | Given observations and models, what latent state is likely? |
| **NET** | Which qualified operations execute, in what order, with what retained evidence? |
| **Scientific Language Runtime** | How does concise human/scientific intent compile into typed query/work contracts? |

NISE constructs **candidate structure**, never physical truth. It does not execute providers, admit evidence, certify causality, or authorize hardware.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Instrument identity

The repository includes a portable `notations.instrument.v1` declaration for the
future semantic capability:

`inference.schematic.construct.v1`.

It is descriptive metadata; it does not itself bind NISE into NET.

## License

MPL-2.0. See `LICENSE`.

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
