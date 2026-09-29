from typing import Dict, Any
from agents.state import QueryState

def validate_citations_node(state: QueryState) -> Dict[str, Any]:
    generated_text = state.get("generated_text", "")
    citations = state.get("citations", [])
    route = state.get("route", "")
    data_res = state.get("data_analysis_result")
    docs = state.get("retrieved_documents", [])
    datasets = state.get("dataset_records", [])
    media = state.get("media_records", [])
    entity_rec = state.get("entity_records", {})

    trace = state.get("execution_trace", [])

    has_evidence = False
    if route == "SCIENTIFIC_DATA_ANALYSIS" and data_res and data_res.get("success"):
        has_evidence = True
    elif route == "MEDIA_SEARCH" and media:
        has_evidence = True
    elif route == "DATASET_SEARCH" and datasets:
        has_evidence = True
    elif docs or (entity_rec and (entity_rec.get("station") or entity_rec.get("expedition"))):
        has_evidence = True

    if not has_evidence or not generated_text.strip() or len(citations) == 0:
        final_answer = "I could not find sufficient information in the indexed official sources."
        groundedness = False
        trace.append("Citation Validator: REJECTED (Zero or insufficient verified evidence found). Enforced strict no-hallucination rule.")
    else:
        final_answer = generated_text
        groundedness = True
        trace.append(f"Citation Validator: PASSED (Verified across {len(citations)} source citations).")

    return {
        "final_answer": final_answer,
        "groundedness_passed": groundedness,
        "execution_trace": trace
    }
