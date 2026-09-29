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
