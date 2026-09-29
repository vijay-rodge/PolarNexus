from typing import Dict, Any
from agents.state import QueryState
from agents.tools.controlled_tools import ControlledPolarTools

def retrieve_rag_node(state: QueryState) -> Dict[str, Any]:
    query = state.get("normalized_query", "")
    entities = state.get("entities", {})
    station = entities.get("station")

    raw_docs = ControlledPolarTools.search_documents(query=query, station=station, top_k=4)
    docs = [d for d in raw_docs if d.get("relevance_score", 0.0) >= 0.40]

    trace = state.get("execution_trace", [])
    trace.append(f"RAG Retrieval: Found {len(docs)} high-confidence relevant chunks from ChromaDB (filtered from {len(raw_docs)} raw candidates)")

    return {
        "retrieved_documents": docs,
        "execution_trace": trace
    }
