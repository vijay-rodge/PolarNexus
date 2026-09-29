from typing import Dict, Any
from agents.state import QueryState
from agents.tools.controlled_tools import ControlledPolarTools

def search_dataset_node(state: QueryState) -> Dict[str, Any]:
    entities = state.get("entities", {})
    station = entities.get("station")
    query = state.get("normalized_query", "")

    datasets = ControlledPolarTools.search_datasets(station_name=station, query=query if not station else None)

    trace = state.get("execution_trace", [])
    trace.append(f"Dataset Search: Found {len(datasets)} matching NPDC datasets")

    return {
        "dataset_records": datasets,
        "execution_trace": trace
    }

def search_media_node(state: QueryState) -> Dict[str, Any]:
    entities = state.get("entities", {})
    station = entities.get("station")

    media = ControlledPolarTools.search_media(station_name=station)

    trace = state.get("execution_trace", [])
    trace.append(f"Media Search: Found {len(media)} photos/media records")

    return {
        "media_records": media,
        "execution_trace": trace
    }

def search_entity_node(state: QueryState) -> Dict[str, Any]:
    entities = state.get("entities", {})
    query = state.get("normalized_query", "")
    station = entities.get("station")
    expedition = entities.get("expedition")

    station_data = None
    expedition_data = None

    if station or state.get("route") == "STATION_SEARCH":
        stations = ControlledPolarTools.search_stations(name_or_query=station or query)
        if stations:
            station_data = stations[0]

    if expedition or state.get("route") == "EXPEDITION_SEARCH":
        expeditions = ControlledPolarTools.search_expeditions(query_term=expedition or query)
        if expeditions:
            expedition_data = expeditions[0]

    companion_docs = ControlledPolarTools.search_documents(query=query, station=station, top_k=3)

    trace = state.get("execution_trace", [])
    trace.append("Entity Search: Retrieved structured metadata & companion docs")

    return {
        "entity_records": {
            "station": station_data,
            "expedition": expedition_data
        },
        "retrieved_documents": companion_docs,
        "execution_trace": trace
    }
