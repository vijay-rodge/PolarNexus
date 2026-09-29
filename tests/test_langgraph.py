import pytest
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from agents.graph import execute_polar_query
from agents.nodes.normalize import normalize_and_extract_entities
from agents.nodes.classify import classify_intent_and_route
from agents.state import QueryState

def test_entity_extraction_node():
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
        "groundedness_passed": False,
        "execution_trace": []
    }
    updated = normalize_and_extract_entities(state)
    entities = updated["entities"]
    assert entities["station"] == "Maitri"
    assert entities["year"] == 2012
    assert entities["parameter"] == "temperature"

def test_intent_classification_routing():
    state: QueryState = {
        "query": "",
        "normalized_query": "what was the average temperature at maitri in 2012?",
        "intent": "",
        "entities": {"station": "Maitri", "year": 2012, "parameter": "temperature"},
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
        "groundedness_passed": False,
        "execution_trace": []
    }
    classified = classify_intent_and_route(state)
    assert classified["intent"] == "SCIENTIFIC_DATA_QUERY"
    assert classified["route"] == "SCIENTIFIC_DATA_ANALYSIS"

def test_full_langgraph_numerical_query():
    res = execute_polar_query("What was the average temperature at Maitri in 2012?")
    assert res["route"] == "SCIENTIFIC_DATA_ANALYSIS"
    assert res["groundedness_passed"] is True
    assert res["data_analysis_result"] is not None
    assert -12.0 < res["data_analysis_result"]["calculated_value"] < -9.0
    assert len(res["citations"]) > 0

def test_full_langgraph_dataset_search_query():
    res = execute_polar_query("What datasets are available for Maitri?")
    assert res["route"] == "DATASET_SEARCH"
    assert res["groundedness_passed"] is True
    assert len(res["dataset_records"]) > 0

def test_full_langgraph_media_query():
    res = execute_polar_query("Show me photographs of Bharati station.")
    assert res["route"] == "MEDIA_SEARCH"
    assert res["groundedness_passed"] is True
    assert len(res["media_records"]) > 0

def test_strict_zero_hallucination_rule():
    res = execute_polar_query("Who won the 2022 FIFA World Cup in Qatar?")
    assert "I could not find sufficient information in the indexed official sources" in res["final_answer"]
    assert res["groundedness_passed"] is False
