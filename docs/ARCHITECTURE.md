# NISE architecture

## Ownership

NISE constructs **candidate investigation structure**.

It does not replace:

- **NET** — execution, composition, retained investigations;
- **FrameMapper** — spatial/temporal/relational representation of known state;
- **State Estimation** — inference of latent system state from observations/models;
- **Evidence & State Management** — evidence admission/canonical state;
- specialist instruments — DSP, calibration, optimization, geometry, simulation.

## Core contract

For a query q, NISE returns

```text
S_q = (V_q, E_q, M_q, C_q, O_q, P_q)
```

with:

- V_q: entities, state variables and geometry;
- E_q: selected typed relations;
- M_q: models;
- C_q: constraints;
- O_q: observations/evidence;
- P_q: semantic operations/instruments.

Every node and edge carries one epistemic label:

`OBSERVED | DERIVED | DECLARED | HYPOTHESIZED`.

Those labels are not truth scores. In particular, `HYPOTHESIZED` is not silently
promoted because it is connected to observed evidence.

## V1 construction algorithm

V1 is intentionally deterministic and non-linguistic:

1. Validate the catalog and query.
2. Seed the graph from explicit `focus_node_ids`.
3. Seed matching OPERATION nodes from explicit semantic capability IDs.
4. Traverse catalog edges up to `max_hops`.
5. Apply the explicit hypothesis policy.
6. Stop at `node_budget`, retaining blocked frontier nodes/reasons.
7. Partition selected nodes into V/M/C/O/P.
8. Retain the selection trace and unresolved capability IDs. Every requested
   operation or focus seed omitted by the budget is recorded in the frontier;
   requested operation seeds excluded by hypothesis policy are recorded too. A
   capability remains unresolved unless an eligible matching operation is selected.
9. Content-address the complete schematic.

The human question string is retained for context but does not drive selection in
V1. A future language/semantic layer may propose focus/capability candidates, but
those proposals must remain explicit inputs and cannot mutate the NISE truth
boundary.

## Authority boundary

Every V1 schematic states:

```json
{
  "candidate_structure": true,
  "physical_truth_established": false,
  "execution_authority": false,
  "state_admission": false,
  "causal_proof": false
}
```

The schematic may be compiled into NET work later, but that is a separate
authority transition.

## Scientific Language Runtime

The companion Notations Scientific Language Runtime should compile concise
scientific intent into `nise.query.v1` or other typed contracts. It should not
contain NISE graph traversal, evidence ranking or state-estimation logic.
