from typing import Dict, Any
from agents.state import QueryState

def classify_intent_and_route(state: QueryState) -> Dict[str, Any]:
    query_lower = state.get("normalized_query", "").lower()
    entities = state.get("entities", {})

    intent = "DOCUMENT_RAG"
    route = "DOCUMENT_RAG"

    numerical_keywords = ["average", "mean", "median", "minimum", "min temp", "maximum", "max temp", 
                          "temperature in", "wind speed in", "trend", "monthly average"]
    has_calc_intent = any(k in query_lower for k in numerical_keywords)
    has_param = entities.get("parameter") is not None

    if has_calc_intent and has_param:
        intent = "SCIENTIFIC_DATA_QUERY"
        route = "SCIENTIFIC_DATA_ANALYSIS"
    elif any(k in query_lower for k in ["photo", "photos", "photograph", "photographs", "picture", "pictures", "image", "images", "gallery", "video", "videos"]):
        intent = "MEDIA_SEARCH"
        route = "MEDIA_SEARCH"
    elif any(k in query_lower for k in ["what datasets", "datasets available", "dataset available", "download data", "weather data is available", "datasets are available"]):
        intent = "DATASET_SEARCH"
        route = "DATASET_SEARCH"
    elif entities.get("audience") == "school_student" or any(k in query_lower for k in ["explain to a school", "for children", "simple explanation"]):
        intent = "EDUCATIONAL_OUTREACH"
        route = "DOCUMENT_RAG"
    elif "expedition" in query_lower and (entities.get("expedition") is not None or any(char.isdigit() for char in query_lower)):
        intent = "EXPEDITION_SEARCH"
        route = "EXPEDITION_SEARCH"
    elif any(k in query_lower for k in ["tell me about", "what is", "where is", "overview of"]) and entities.get("station"):
        intent = "STATION_SEARCH"
        route = "STATION_SEARCH"

    trace = state.get("execution_trace", [])
    trace.append(f"Classify: Intent='{intent}', Selected Route='{route}'")

    return {
        "intent": intent,
        "route": route,
        "execution_trace": trace
    }
