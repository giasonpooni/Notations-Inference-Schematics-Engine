"""Deterministic NISE schematic compiler.

V1 does not perform NLP retrieval. Human question text is retained, while graph
selection is driven by explicit focus identities, requested semantic capabilities,
epistemic policy, bounded graph traversal and a node budget.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy

from .contracts import (
    EPISTEMIC,
    content_identity,
    validate_catalog,
    validate_query,
    validate_schematic,
)


PARTITIONS = {
    "ENTITY": "V_q",
    "STATE_VARIABLE": "V_q",
    "GEOMETRY": "V_q",
    "MODEL": "M_q",
    "CONSTRAINT": "C_q",
    "OBSERVATION": "O_q",
    "OPERATION": "P_q",
}


def compile_schematic(catalog: dict, query: dict) -> dict:
    catalog = validate_catalog(catalog)
    query = validate_query(query)

    nodes = {item["node_id"]: item for item in catalog["nodes"]}
    for node_id in query["focus_node_ids"]:
        if node_id not in nodes:
            raise ValueError(f"Focus node is not present in the system catalog: {node_id}")
        if nodes[node_id]["status"] == "HYPOTHESIZED" and not query["include_hypotheses"]:
            raise ValueError("A hypothesized focus requires include_hypotheses=true")

    operation_nodes = {}
    for node in catalog["nodes"]:
        if node["kind"] == "OPERATION":
            capability = node["attributes"]["semantic_capability"]
            operation_nodes.setdefault(capability, []).append(node["node_id"])

    adjacency = {node_id: [] for node_id in nodes}
    for edge in catalog["edges"]:
        adjacency[edge["source"]].append((edge["target"], edge))
        if not edge["directional"]:
            adjacency[edge["target"]].append((edge["source"], edge))

    seed_reasons: dict[str, str] = {node_id: "focus" for node_id in query["focus_node_ids"]}
    unresolved = []
    for capability in query["requested_capabilities"]:
        matches = sorted(operation_nodes.get(capability, []))
        if not matches:
            unresolved.append(capability)
            continue
        for node_id in matches:
            if nodes[node_id]["status"] == "HYPOTHESIZED" and not query["include_hypotheses"]:
                continue
            seed_reasons.setdefault(node_id, "requested_capability")

    queue = deque()
    depth: dict[str, int] = {}
    reason: dict[str, str] = {}
    for node_id in sorted(seed_reasons):
        if len(depth) >= query["node_budget"]:
            break
        depth[node_id] = 0
        reason[node_id] = seed_reasons[node_id]
        queue.append(node_id)

    frontier: dict[tuple[str, str], dict] = {}
    while queue:
        current = queue.popleft()
        current_depth = depth[current]
        for target, edge in sorted(adjacency[current], key=lambda item: (item[0], item[1]["edge_id"])):
            if edge["status"] == "HYPOTHESIZED" and not query["include_hypotheses"]:
                frontier[(target, "hypothesis_policy")] = {
                    "node_id": target,
                    "blocked_by": "hypothesis_policy",
                }
                continue
            if nodes[target]["status"] == "HYPOTHESIZED" and not query["include_hypotheses"]:
                frontier[(target, "hypothesis_policy")] = {
                    "node_id": target,
                    "blocked_by": "hypothesis_policy",
                }
                continue
            if target in depth:
                continue
            if current_depth >= query["max_hops"]:
                frontier[(target, "hop_limit")] = {"node_id": target, "blocked_by": "hop_limit"}
                continue
            if len(depth) >= query["node_budget"]:
                frontier[(target, "node_budget")] = {"node_id": target, "blocked_by": "node_budget"}
                continue
            depth[target] = current_depth + 1
            reason[target] = "reachable"
            queue.append(target)

    selected = set(depth)
    selected_edges = []
    for edge in catalog["edges"]:
        if edge["source"] not in selected or edge["target"] not in selected:
            continue
        if edge["status"] == "HYPOTHESIZED" and not query["include_hypotheses"]:
            continue
        selected_edges.append(deepcopy(edge))

    result = {
        "schema": "nise.inference-schematic.v1",
        "schematic_id": None,
        "query": deepcopy(query),
        "catalog_id": catalog["catalog_id"],
        "catalog_digest": content_identity(catalog),
        "V_q": [],
        "E_q": sorted(selected_edges, key=lambda item: item["edge_id"]),
        "M_q": [],
        "C_q": [],
        "O_q": [],
        "P_q": [],
        "selection_trace": [
            {"node_id": node_id, "depth": depth[node_id], "reason": reason[node_id]}
            for node_id in sorted(selected, key=lambda item: (depth[item], item))
        ],
        "unresolved_capabilities": sorted(unresolved),
        "frontier": sorted(frontier.values(), key=lambda item: (item["blocked_by"], item["node_id"])),
        "claims": {
            "candidate_structure": True,
            "physical_truth_established": False,
            "execution_authority": False,
            "state_admission": False,
            "causal_proof": False,
        },
    }
    for node_id in sorted(selected):
        node = deepcopy(nodes[node_id])
        result[PARTITIONS[node["kind"]]].append(node)

    result["schematic_id"] = content_identity(
        {key: value for key, value in result.items() if key != "schematic_id"}
    )
    validate_schematic(result)
    return result


def inspect_schematic(value: dict) -> dict:
    value = validate_schematic(value)
    return {
        "schema": "nise.schematic-inspection.v1",
        "schematic_id": value["schematic_id"],
        "query_id": value["query"]["query_id"],
        "catalog_id": value["catalog_id"],
        "counts": {
            "V_q": len(value["V_q"]),
            "E_q": len(value["E_q"]),
            "M_q": len(value["M_q"]),
            "C_q": len(value["C_q"]),
            "O_q": len(value["O_q"]),
            "P_q": len(value["P_q"]),
        },
        "unresolved_capabilities": deepcopy(value["unresolved_capabilities"]),
        "frontier_count": len(value["frontier"]),
        "candidate_structure": True,
        "physical_truth_established": False,
        "execution_authority": False,
    }
