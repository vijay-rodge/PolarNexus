from typing import TypedDict, List, Dict, Any, Optional

class QueryState(TypedDict):
    query: str
    normalized_query: str
    intent: str
    entities: Dict[str, Any]
    route: str
    
    retrieved_documents: List[Dict[str, Any]]
    dataset_records: List[Dict[str, Any]]
    data_analysis_result: Optional[Dict[str, Any]]
    media_records: List[Dict[str, Any]]
    entity_records: Optional[Dict[str, Any]]
    
    raw_evidence_summary: Dict[str, Any]
    generated_text: str
    final_answer: str
    citations: List[Dict[str, Any]]
    coordinates: List[Dict[str, Any]]
    extracted_figures: List[Dict[str, Any]]
    response_time_ms: float
    groundedness_passed: bool
    execution_trace: List[str]
