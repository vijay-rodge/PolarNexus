import re
from typing import Dict, Any
from agents.state import QueryState
from config.constants import STATIONS

def normalize_and_extract_entities(state: QueryState) -> Dict[str, Any]:
    raw_query = state.get("query", "").strip()
    normalized = re.sub(r'\s+', ' ', raw_query).strip()

    entities = {
        "station": None,
        "year": None,
        "parameter": None,
        "expedition": None,
        "audience": "general"
    }

    norm_lower = normalized.lower()
    for station_key, s_data in STATIONS.items():
        s_name = s_data["name"].lower()
        if s_name in norm_lower:
            entities["station"] = s_data["name"]
            break

    year_match = re.search(r'\b(19[89]\d|20[0-3]\d)\b', normalized)
    if year_match:
        entities["year"] = int(year_match.group(1))

    params_map = {
        "temperature": ["temperature", "temp", "thermal", "cooling", "warming"],
        "wind_speed": ["wind speed", "wind", "winds", "gale", "blizzard"],
        "atmospheric_pressure": ["pressure", "barometric", "barometer"],
        "relative_humidity": ["humidity", "moisture"],
        "solar_radiation": ["solar", "radiation", "irradiance", "sunlight"]
    }
    for canonical_param, keywords in params_map.items():
        if any(k in norm_lower for k in keywords):
            entities["parameter"] = canonical_param
            break

    exp_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s+(arctic|antarctic)\s+expedition', norm_lower)
    if exp_match:
        exp_num = exp_match.group(1)
        region = exp_match.group(2).capitalize()
        entities["expedition"] = f"{exp_num}th Indian {region} Expedition"

    if any(k in norm_lower for k in ["student", "school", "child", "kids", "simple words", "explain to a 10 year old"]):
        entities["audience"] = "school_student"

    trace = state.get("execution_trace", [])
    trace.append(f"Normalize: Extracted entities -> {entities}")

    return {
        "normalized_query": normalized,
        "entities": entities,
        "execution_trace": trace
    }
