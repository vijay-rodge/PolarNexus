from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="User natural language question")
    audience: Optional[str] = Field("general", description="Target audience: general, school_student, researcher")

class CitationItem(BaseModel):
    citation_id: int
    source_name: str
    document_id: Optional[str] = None
    station: Optional[str] = None
    section: Optional[str] = None
    page: Optional[int] = None
    url: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    intent: str
    route: str
    entities: Dict[str, Any]
    final_answer: str
    citations: List[Dict[str, Any]]
    groundedness_passed: bool
    data_analysis_result: Optional[Dict[str, Any]] = None
    media_records: Optional[List[Dict[str, Any]]] = None
    dataset_records: Optional[List[Dict[str, Any]]] = None
    execution_trace: List[str]

class AnalysisRequest(BaseModel):
    station: str = Field(..., example="Maitri")
    parameter: str = Field("temperature", example="temperature")
    operation: str = Field("mean", example="mean")
    year: Optional[int] = Field(2012, example=2012)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class StationResponse(BaseModel):
    station_id: str
    name: str
    region: str
    location: Optional[str]
    latitude: float
    longitude: float
    commissioned_year: int
    status: str
    facilities: Optional[List[str]]
    overview: Optional[str]
    image_url: Optional[str]
