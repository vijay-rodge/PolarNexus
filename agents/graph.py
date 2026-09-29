import time
from langgraph.graph import StateGraph, START, END
from agents.state import QueryState
from agents.nodes.normalize import normalize_and_extract_entities
from agents.nodes.classify import classify_intent_and_route
from agents.nodes.retrieve_rag import retrieve_rag_node
from agents.nodes.analyze_data import analyze_scientific_data_node
from agents.nodes.search_nodes import search_dataset_node, search_media_node, search_entity_node
from agents.nodes.generate_answer import ResponseGenerator
from agents.nodes.validate_citations import validate_citations_node

def route_selector(state: QueryState) -> str:
    route = state.get("route", "DOCUMENT_RAG")
    if route == "SCIENTIFIC_DATA_ANALYSIS":
        return "analyze_data"
    elif route == "MEDIA_SEARCH":
        return "search_media"
    elif route == "DATASET_SEARCH":
        return "search_dataset"
    elif route in ["STATION_SEARCH", "EXPEDITION_SEARCH"]:
        return "search_entity"
    else:
        return "retrieve_rag"

def generate_node(state: QueryState):
    return ResponseGenerator.generate(state)

def create_polar_query_graph():
    builder = StateGraph(QueryState)

    builder.add_node("normalize", normalize_and_extract_entities)
    builder.add_node("classify", classify_intent_and_route)
    builder.add_node("retrieve_rag", retrieve_rag_node)
    builder.add_node("analyze_data", analyze_scientific_data_node)
    builder.add_node("search_dataset", search_dataset_node)
    builder.add_node("search_media", search_media_node)
    builder.add_node("search_entity", search_entity_node)
    builder.add_node("generate_answer", generate_node)
    builder.add_node("validate_citations", validate_citations_node)

    builder.add_edge(START, "normalize")
    builder.add_edge("normalize", "classify")

    builder.add_conditional_edges(
        "classify",
        route_selector,
        {
            "analyze_data": "analyze_data",
            "search_media": "search_media",
            "search_dataset": "search_dataset",
            "search_entity": "search_entity",
            "retrieve_rag": "retrieve_rag"
        }
    )

    builder.add_edge("analyze_data", "generate_answer")
    builder.add_edge("search_media", "generate_answer")
    builder.add_edge("search_dataset", "generate_answer")
    builder.add_edge("search_entity", "generate_answer")
    builder.add_edge("retrieve_rag", "generate_answer")

    builder.add_edge("generate_answer", "validate_citations")
    builder.add_edge("validate_citations", END)

    return builder.compile()

polar_graph = create_polar_query_graph()

def execute_polar_query(query_text: str) -> QueryState:
    initial_state: QueryState = {
        "query": query_text,
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
    start_time = time.perf_counter()
    result = polar_graph.invoke(initial_state)
    end_time = time.perf_counter()
    elapsed_ms = round((end_time - start_time) * 1000.0, 2)
    result["response_time_ms"] = elapsed_ms
    trace = result.get("execution_trace", [])
    trace.append(f"Execution Timing: Completed end-to-end pipeline in {elapsed_ms} ms")
    result["execution_trace"] = trace
    return result
