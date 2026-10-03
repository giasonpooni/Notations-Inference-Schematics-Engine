from copy import deepcopy
import json
from pathlib import Path

import pytest

from nise.compiler import compile_schematic, inspect_schematic
from nise.contracts import content_identity, validate_catalog, validate_query, validate_schematic

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "examples" / name).read_text())


def test_canonical_bearing_schematic_is_query_specific_and_bounded():
    result = compile_schematic(load("bearing_catalog.json"), load("bearing_query.json"))
    validate_schematic(result)
    assert result["claims"]["candidate_structure"] is True
    assert result["claims"]["physical_truth_established"] is False
    assert result["claims"]["execution_authority"] is False
    assert "fault.classify.v1" in result["unresolved_capabilities"]
    assert all(node["status"] != "HYPOTHESIZED" for key in ("V_q","M_q","C_q","O_q","P_q") for node in result[key])
    assert result["schematic_id"] == content_identity({k:v for k,v in result.items() if k != "schematic_id"})


def test_requested_capability_is_seeded_even_when_not_reachable_from_focus():
    catalog = load("bearing_catalog.json")
    query = load("bearing_query.json")
    query["max_hops"] = 0
    result = compile_schematic(catalog, query)
    operations = {node["attributes"]["semantic_capability"] for node in result["P_q"]}
    assert "signal.spectrum.v1" in operations
    assert "state.estimate.v1" in operations
    trace = {row["node_id"]: row for row in result["selection_trace"]}
    assert trace["op.spectrum"]["reason"] == "requested_capability"


def test_hypothesis_policy_is_explicit_and_frontier_retained():
    catalog = load("bearing_catalog.json")
    query = load("bearing_query.json")
    result = compile_schematic(catalog, query)
    assert any(row["blocked_by"] == "hypothesis_policy" for row in result["frontier"])
    query["include_hypotheses"] = True
    result = compile_schematic(catalog, query)
    assert any(node["node_id"] == "bearing_04.hidden-damage" for node in result["V_q"])


def test_question_text_does_not_secretly_select_nodes():
    catalog = load("bearing_catalog.json")
    query = load("bearing_query.json")
    left = compile_schematic(catalog, query)
    query["question"] = "Completely different natural-language wording mentioning hidden damage."
    right = compile_schematic(catalog, query)
    def selected(value):
        return sorted(node["node_id"] for key in ("V_q","M_q","C_q","O_q","P_q") for node in value[key])
    assert selected(left) == selected(right)


def test_node_budget_retains_frontier_instead_of_silent_drop():
    catalog = load("bearing_catalog.json")
    query = load("bearing_query.json")
    query["node_budget"] = 3
    result = compile_schematic(catalog, query)
    assert sum(len(result[key]) for key in ("V_q","M_q","C_q","O_q","P_q")) == 3
    assert any(row["blocked_by"] == "node_budget" for row in result["frontier"])


@pytest.mark.parametrize("field", ["missing_focus", "bad_capability", "too_many_hops", "hypothesis_focus"])
def test_invalid_or_unauthorized_query_refuses(field):
    catalog = load("bearing_catalog.json")
    query = load("bearing_query.json")
    if field == "missing_focus":
        query["focus_node_ids"] = ["missing"]
    elif field == "bad_capability":
        query["requested_capabilities"] = ["spectrum"]
    elif field == "too_many_hops":
        query["max_hops"] = 99
    else:
        query["focus_node_ids"] = ["bearing_04.hidden-damage"]
        query["include_hypotheses"] = False
    with pytest.raises(ValueError):
        compile_schematic(catalog, query)


@pytest.mark.parametrize("fault", ["duplicate_node", "bad_edge", "operation_without_capability", "bad_status"])
def test_catalog_integrity_refuses(fault):
    catalog = load("bearing_catalog.json")
    if fault == "duplicate_node":
        catalog["nodes"].append(deepcopy(catalog["nodes"][0]))
    elif fault == "bad_edge":
        catalog["edges"][0]["target"] = "missing"
    elif fault == "operation_without_capability":
        catalog["nodes"][5]["attributes"] = {}
    else:
        catalog["edges"][0]["status"] = "TRUE"
    with pytest.raises(ValueError):
        validate_catalog(catalog)


def test_inspection_is_data_only_summary():
    result = compile_schematic(load("bearing_catalog.json"), load("bearing_query.json"))
    inspection = inspect_schematic(result)
    assert inspection["schematic_id"] == result["schematic_id"]
    assert inspection["physical_truth_established"] is False
    assert inspection["execution_authority"] is False


@pytest.mark.parametrize("budget", [1, 2, 3, 4])
def test_disconnected_requested_seeds_are_all_selected_or_accounted_for(budget):
    catalog = load("bearing_catalog.json")
    catalog["edges"] = []
    query = load("bearing_query.json")
    query["focus_node_ids"] = ["bearing_04", "bearing_04.vibration"]
    query["requested_capabilities"] = ["signal.spectrum.v1", "state.estimate.v1"]
    query["max_hops"] = 0
    query["node_budget"] = budget
    result = compile_schematic(catalog, query)
    selected = {row["node_id"] for row in result["selection_trace"]}
    seeds = {"bearing_04", "bearing_04.vibration", "op.spectrum", "op.state-estimate"}
    blocked = {row["node_id"] for row in result["frontier"] if row["blocked_by"] == "node_budget"}
    assert len(selected) == budget
    assert blocked == seeds - selected
    assert set(result["unresolved_capabilities"]) == {
        capability for node_id, capability in [
            ("op.spectrum", "signal.spectrum.v1"),
            ("op.state-estimate", "state.estimate.v1"),
        ] if node_id not in selected
    }
    reordered = deepcopy(catalog)
    reordered["nodes"].reverse()
    assert compile_schematic(reordered, query)["selection_trace"] == result["selection_trace"]
    assert compile_schematic(reordered, query)["frontier"] == result["frontier"]


def test_requested_hypothesized_operation_is_explicitly_blocked_and_unresolved():
    catalog = load("bearing_catalog.json")
    catalog["edges"] = []
    for node in catalog["nodes"]:
        if node["node_id"] == "op.spectrum":
            node["status"] = "HYPOTHESIZED"
    query = load("bearing_query.json")
    query["requested_capabilities"] = ["signal.spectrum.v1"]
    result = compile_schematic(catalog, query)
    assert result["unresolved_capabilities"] == ["signal.spectrum.v1"]
    assert result["frontier"] == [{"node_id": "op.spectrum", "blocked_by": "hypothesis_policy"}]
    query["include_hypotheses"] = True
    result = compile_schematic(catalog, query)
    assert result["unresolved_capabilities"] == []
    assert result["P_q"][0]["node_id"] == "op.spectrum"


def test_capability_with_an_eligible_implementation_is_resolved_despite_blocked_alternative():
    catalog = load("bearing_catalog.json")
    catalog["edges"] = []
    alternative = deepcopy(next(node for node in catalog["nodes"] if node["node_id"] == "op.spectrum"))
    alternative["node_id"] = "op.spectrum-hypothesis"
    alternative["status"] = "HYPOTHESIZED"
    catalog["nodes"].append(alternative)
    query = load("bearing_query.json")
    query["requested_capabilities"] = ["signal.spectrum.v1"]
    result = compile_schematic(catalog, query)
    assert result["unresolved_capabilities"] == []
    assert {node["node_id"] for node in result["P_q"]} == {"op.spectrum"}
    assert result["frontier"] == [{"node_id": "op.spectrum-hypothesis", "blocked_by": "hypothesis_policy"}]
