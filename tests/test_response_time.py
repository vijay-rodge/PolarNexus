import time
import pytest
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from agents.graph import execute_polar_query
from agents.nodes.normalize import normalize_and_extract_entities
from agents.nodes.classify import classify_intent_and_route
from agents.state import QueryState

def test_intent_routing_latency():
    """Validates that regex and rule-based entity extraction and routing is sub-100ms."""
    state: QueryState = {
        "query": "What was the average temperature at Maitri in 2012?",
        "normalized_query": "",
        "intent": "",
        "entities": {},
        "route": "",
        "retrieved_documents": [],
        "dataset_records": [],
        "data_analysis_result": None,
        "media_records": [],
        "entity_records": None,
        "raw_evidence_summary": {},
        "generated_text": "",
        "final_answer": "",
        "citations": [],
        "coordinates": [],
        "extracted_figures": [],
        "response_time_ms": 0.0,
        "groundedness_passed": False,
        "execution_trace": []
    }

    t0 = time.perf_counter()
    res_norm = normalize_and_extract_entities(state)
    state.update(res_norm)
    res_class = classify_intent_and_route(state)
    state.update(res_class)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert state["route"] == "SCIENTIFIC_DATA_ANALYSIS"
    assert state["entities"]["station"] == "Maitri"
    assert state["entities"]["year"] == 2012
    assert elapsed_ms < 100.0, f"Routing took too long: {elapsed_ms:.2f} ms"

def test_numerical_analysis_response_time():
    """
    Validates end-to-end response time for numerical queries (Maitri 2012 AWS temperature).
    Deterministic pandas execution should complete within SLA (< 2500 ms on standard CPU).
    """
    t_start = time.perf_counter()
    res = execute_polar_query("What was the average temperature at Maitri in 2012?")
    t_end = time.perf_counter()
    measured_ms = (t_end - t_start) * 1000.0

    assert res["route"] == "SCIENTIFIC_DATA_ANALYSIS"
    assert res["groundedness_passed"] is True
    assert "response_time_ms" in res
    assert res["response_time_ms"] > 0.0

    # Verify measured wall-clock time aligns closely with reported response_time_ms
    assert abs(measured_ms - res["response_time_ms"]) < 100.0
    assert res["response_time_ms"] < 2500.0, f"Numerical analysis exceeded SLA: {res['response_time_ms']} ms"

def test_dataset_search_response_time():
    """Validates response time for NPDC structured dataset searches."""
    res = execute_polar_query("What datasets are available for Maitri?")
    assert res["route"] == "DATASET_SEARCH"
    assert res["response_time_ms"] > 0.0
    assert res["response_time_ms"] < 2500.0, f"Dataset search exceeded SLA: {res['response_time_ms']} ms"

def test_media_search_response_time():
    """Validates response time for media and photograph discovery."""
    res = execute_polar_query("Show me photographs of Bharati station.")
    assert res["route"] == "MEDIA_SEARCH"
    assert res["response_time_ms"] > 0.0
    assert res["response_time_ms"] < 2500.0, f"Media search exceeded SLA: {res['response_time_ms']} ms"

def test_response_time_recorded_in_trace():
    """Verifies that the execution trace includes granular performance timing."""
    res = execute_polar_query("Who won the 2022 FIFA World Cup in Qatar?")
    trace = res.get("execution_trace", [])
    timing_entries = [entry for entry in trace if "Execution Timing" in entry]
    assert len(timing_entries) > 0, "Execution timing was not recorded in trace"
    assert f"{res['response_time_ms']} ms" in timing_entries[0]
