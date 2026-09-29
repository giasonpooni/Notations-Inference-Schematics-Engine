"""Data-only NISE contracts.

NISE retains candidate investigation structure. It does not authenticate evidence,
prove causality, execute providers, estimate state, or authorize physical action.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import re
from typing import Any

MAX_BYTES = 2 * 1024 * 1024
MAX_NODES = 1024
MAX_EDGES = 4096
MAX_EVIDENCE_REFS = 64
MAX_HOPS = 6
MAX_SELECTED_NODES = 256

NODE_KINDS = {
    "ENTITY",
    "STATE_VARIABLE",
    "GEOMETRY",
    "MODEL",
    "CONSTRAINT",
    "OBSERVATION",
    "OPERATION",
}
EPISTEMIC = {"OBSERVED", "DERIVED", "DECLARED", "HYPOTHESIZED"}
CAPABILITY = re.compile(r"[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+\.v[1-9][0-9]*$")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
CONTENT_REF = re.compile(r"sha256:[0-9a-f]{64}$")


def text(value: Any, *, maximum: int = 512) -> str:
    if type(value) is not str or not value.strip() or len(value) > maximum:
        raise ValueError("Require bounded nonempty text")
    return value


def identifier(value: Any) -> str:
    if type(value) is not str or IDENTIFIER.fullmatch(value) is None:
        raise ValueError("Invalid bounded identifier")
    return value


def content_ref(value: Any) -> str:
    if type(value) is not str or CONTENT_REF.fullmatch(value) is None:
        raise ValueError("Evidence references must be canonical SHA256 identities")
    return value


def number(value: Any) -> float:
    if type(value) not in (int, float) or isinstance(value, bool):
        raise ValueError("Require a finite JSON number")
    value = float(value)
    if not math.isfinite(value) or abs(value) > 1e150:
        raise ValueError("Require a finite bounded JSON number")
    return value


def json_tree(value: Any, depth: int = 0) -> None:
    if depth > 24:
        raise ValueError("JSON nesting exceeds bound")
    if value is None or type(value) is bool:
        return
    if type(value) is str:
        if len(value) > 65536:
            raise ValueError("JSON string exceeds bound")
        return
    if type(value) in (int, float):
        number(value)
        return
    if type(value) is list:
        if len(value) > 4096:
            raise ValueError("JSON array exceeds bound")
        for item in value:
            json_tree(item, depth + 1)
        return
    if type(value) is dict:
        if len(value) > 2048:
            raise ValueError("JSON object exceeds bound")
        for key, item in value.items():
            text(key)
            json_tree(item, depth + 1)
        return
    raise ValueError("Require bounded JSON-compatible data")


def canonical_json(value: Any) -> str:
    json_tree(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def content_identity(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _keys(value: Any, expected: set[str]) -> None:
    if type(value) is not dict or set(value) != expected:
        raise ValueError("Unexpected or missing contract fields")


def _evidence_refs(value: Any) -> list[str]:
    if type(value) is not list or len(value) > MAX_EVIDENCE_REFS:
        raise ValueError("Evidence references exceed bound")
    result = [content_ref(item) for item in value]
    if len(result) != len(set(result)):
        raise ValueError("Duplicate evidence reference")
    return result


def _status(value: Any) -> str:
    if value not in EPISTEMIC:
        raise ValueError("Unknown epistemic status")
    return value


def _node(value: dict) -> dict:
    _keys(value, {"node_id", "kind", "label", "status", "attributes", "evidence_refs"})
    identifier(value["node_id"])
    if value["kind"] not in NODE_KINDS:
        raise ValueError("Unknown NISE node kind")
    text(value["label"])
    _status(value["status"])
    if type(value["attributes"]) is not dict:
        raise ValueError("Node attributes must be an object")
    json_tree(value["attributes"])
    _evidence_refs(value["evidence_refs"])
    if value["kind"] == "OPERATION":
        capability = value["attributes"].get("semantic_capability")
        if type(capability) is not str or CAPABILITY.fullmatch(capability) is None:
            raise ValueError("Operation nodes require a versioned semantic_capability")
    return deepcopy(value)


def _edge(value: dict, node_ids: set[str]) -> dict:
    _keys(value, {
        "edge_id", "source", "target", "relation", "status",
        "directional", "evidence_refs", "attributes",
    })
    identifier(value["edge_id"])
    identifier(value["source"])
    identifier(value["target"])
    if value["source"] == value["target"]:
        raise ValueError("Self-edges are not part of the V1 schematic contract")
    if value["source"] not in node_ids or value["target"] not in node_ids:
        raise ValueError("Edge endpoint is not present in catalog nodes")
    text(value["relation"])
    _status(value["status"])
    if type(value["directional"]) is not bool:
        raise ValueError("directional must be boolean")
    _evidence_refs(value["evidence_refs"])
    if type(value["attributes"]) is not dict:
        raise ValueError("Edge attributes must be an object")
    json_tree(value["attributes"])
    return deepcopy(value)


def validate_catalog(value: dict) -> dict:
    _keys(value, {"schema", "catalog_id", "nodes", "edges", "metadata"})
    if value["schema"] != "nise.system-catalog.v1":
        raise ValueError("Unsupported NISE system catalog")
    identifier(value["catalog_id"])
    if type(value["nodes"]) is not list or not 1 <= len(value["nodes"]) <= MAX_NODES:
        raise ValueError("Catalog requires 1..1024 nodes")
    if type(value["edges"]) is not list or len(value["edges"]) > MAX_EDGES:
        raise ValueError("Catalog edge count exceeds bound")
    nodes = [_node(item) for item in value["nodes"]]
    node_ids = [item["node_id"] for item in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Duplicate node identity")
    edges = [_edge(item, set(node_ids)) for item in value["edges"]]
    edge_ids = [item["edge_id"] for item in edges]
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError("Duplicate edge identity")
    if type(value["metadata"]) is not dict:
        raise ValueError("Catalog metadata must be an object")
    json_tree(value["metadata"])
    return deepcopy(value)


def validate_query(value: dict) -> dict:
    _keys(value, {
        "schema", "query_id", "question", "focus_node_ids",
        "requested_capabilities", "max_hops", "node_budget",
        "include_hypotheses",
    })
    if value["schema"] != "nise.query.v1":
        raise ValueError("Unsupported NISE query")
    identifier(value["query_id"])
    text(value["question"], maximum=8192)
    if type(value["focus_node_ids"]) is not list or not value["focus_node_ids"]:
        raise ValueError("Query requires at least one explicit focus node")
    focus = [identifier(item) for item in value["focus_node_ids"]]
    if len(focus) != len(set(focus)) or len(focus) > 64:
        raise ValueError("Focus nodes must be unique and bounded")
    if type(value["requested_capabilities"]) is not list or len(value["requested_capabilities"]) > 64:
        raise ValueError("Requested capabilities exceed bound")
    capabilities = []
    for item in value["requested_capabilities"]:
        if type(item) is not str or CAPABILITY.fullmatch(item) is None:
            raise ValueError("Requested capabilities must be versioned semantic IDs")
        capabilities.append(item)
    if len(capabilities) != len(set(capabilities)):
        raise ValueError("Duplicate requested capability")
    if type(value["max_hops"]) is not int or not 0 <= value["max_hops"] <= MAX_HOPS:
        raise ValueError("max_hops must be in 0..6")
    if type(value["node_budget"]) is not int or not 1 <= value["node_budget"] <= MAX_SELECTED_NODES:
        raise ValueError("node_budget must be in 1..256")
    if type(value["include_hypotheses"]) is not bool:
        raise ValueError("include_hypotheses must be boolean")
    return deepcopy(value)


def validate_schematic(value: dict) -> dict:
    _keys(value, {
        "schema", "schematic_id", "query", "catalog_id", "catalog_digest",
        "V_q", "E_q", "M_q", "C_q", "O_q", "P_q",
        "selection_trace", "unresolved_capabilities", "frontier",
        "claims",
    })
    if value["schema"] != "nise.inference-schematic.v1":
        raise ValueError("Unsupported inference schematic")
    validate_query(value["query"])
    identifier(value["catalog_id"])
    content_ref(value["catalog_digest"])
    content_ref(value["schematic_id"])
    partitions = {
        "V_q": {"ENTITY", "STATE_VARIABLE", "GEOMETRY"},
        "M_q": {"MODEL"},
        "C_q": {"CONSTRAINT"},
        "O_q": {"OBSERVATION"},
        "P_q": {"OPERATION"},
    }
    all_nodes = []
    for key, kinds in partitions.items():
        if type(value[key]) is not list:
            raise ValueError("Schematic node partitions must be arrays")
        for item in value[key]:
            node = _node(item)
            if node["kind"] not in kinds:
                raise ValueError("Node appears in the wrong schematic partition")
            all_nodes.append(node)
    node_ids = [item["node_id"] for item in all_nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Schematic duplicates a node across partitions")
    if len(node_ids) > value["query"]["node_budget"]:
        raise ValueError("Schematic exceeds query node budget")
    if type(value["E_q"]) is not list or len(value["E_q"]) > MAX_EDGES:
        raise ValueError("Schematic edge set exceeds bound")
    edges = [_edge(item, set(node_ids)) for item in value["E_q"]]
    if len({item["edge_id"] for item in edges}) != len(edges):
        raise ValueError("Duplicate schematic edge")
    if type(value["selection_trace"]) is not list or len(value["selection_trace"]) != len(node_ids):
        raise ValueError("Selection trace must cover every selected node exactly once")
    traced = set()
    for item in value["selection_trace"]:
        _keys(item, {"node_id", "depth", "reason"})
        node_id = identifier(item["node_id"])
        if node_id in traced or node_id not in set(node_ids):
            raise ValueError("Selection trace identity mismatch")
        traced.add(node_id)
        if type(item["depth"]) is not int or not 0 <= item["depth"] <= MAX_HOPS:
            raise ValueError("Selection trace depth is invalid")
        if item["reason"] not in {"focus", "requested_capability", "reachable"}:
            raise ValueError("Unknown selection reason")
    if type(value["unresolved_capabilities"]) is not list:
        raise ValueError("unresolved_capabilities must be an array")
    for item in value["unresolved_capabilities"]:
        if type(item) is not str or CAPABILITY.fullmatch(item) is None:
            raise ValueError("Invalid unresolved capability identity")
    if type(value["frontier"]) is not list:
        raise ValueError("frontier must be an array")
    for item in value["frontier"]:
        _keys(item, {"node_id", "blocked_by"})
        identifier(item["node_id"])
        if item["blocked_by"] not in {"hop_limit", "node_budget", "hypothesis_policy"}:
            raise ValueError("Unknown frontier reason")
    claims = value["claims"]
    _keys(claims, {
        "candidate_structure", "physical_truth_established",
        "execution_authority", "state_admission", "causal_proof",
    })
    if claims != {
        "candidate_structure": True,
        "physical_truth_established": False,
        "execution_authority": False,
        "state_admission": False,
        "causal_proof": False,
    }:
        raise ValueError("Schematic authority/truth claims exceed NISE V1")
    expected = content_identity({key: item for key, item in value.items() if key != "schematic_id"})
    if value["schematic_id"] != expected:
        raise ValueError("Schematic content identity mismatch")
    return deepcopy(value)
