from typing import Dict, Any
from agents.state import QueryState
from agents.tools.controlled_tools import ControlledPolarTools

def analyze_scientific_data_node(state: QueryState) -> Dict[str, Any]:
    query_lower = state.get("normalized_query", "").lower()
    entities = state.get("entities", {})
    
    station = entities.get("station") or "Maitri"
    parameter = entities.get("parameter") or "temperature"
    year = entities.get("year") or 2012

    operation = "mean"
    if "median" in query_lower:
        operation = "median"
    elif "minimum" in query_lower or "min" in query_lower:
        operation = "min"
    elif "maximum" in query_lower or "max" in query_lower:
        operation = "max"
    elif "trend" in query_lower:
        operation = "trend_slope"
    elif "monthly" in query_lower:
        operation = "monthly_average"
    elif "count" in query_lower or "how many" in query_lower:
        operation = "count"

    result = ControlledPolarTools.analyze_dataset(
        station=station,
        parameter=parameter,
        operation=operation,
        year=year
    )

    trace = state.get("execution_trace", [])
    trace.append(f"Data Analysis: Executed {operation} on {station} {parameter} (Year: {year}) -> Success={result.get('success')}")

    return {
        "data_analysis_result": result,
        "execution_trace": trace
    }
