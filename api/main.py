from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from config.settings import settings
from api.schemas import QueryRequest, QueryResponse, AnalysisRequest, StationResponse
from agents.graph import execute_polar_query
from agents.tools.controlled_tools import ControlledPolarTools
from database.connection import SessionLocal
from database.models import Station, Expedition, Dataset, MediaRecord, IngestionLog, MLModelRegistry
from sqlalchemy.orm import Session

app = FastAPI(
    title="Polar Science Knowledge & Outreach API",
    description="Backend services for SIH PS 26063: Integrated Polar Science Outreach, Knowledge Repository and Media Dissemination Portal",
    version=settings.APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.post("/api/query", response_model=QueryResponse)
def query_polar_assistant(req: QueryRequest):
    try:
        result = execute_polar_query(req.query)
        return QueryResponse(
            query=req.query,
            intent=result.get("intent", "UNKNOWN"),
            route=result.get("route", "UNKNOWN"),
            entities=result.get("entities", {}),
            final_answer=result.get("final_answer", ""),
            citations=result.get("citations", []),
            groundedness_passed=result.get("groundedness_passed", False),
            data_analysis_result=result.get("data_analysis_result"),
            media_records=result.get("media_records"),
            dataset_records=result.get("dataset_records"),
            execution_trace=result.get("execution_trace", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
def analyze_dataset_parameter(req: AnalysisRequest):
    res = ControlledPolarTools.analyze_dataset(
        station=req.station,
        parameter=req.parameter,
        operation=req.operation,
        year=req.year,
        start_date=req.start_date,
        end_date=req.end_date
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Analysis failed"))
    return res

@app.get("/api/stations", response_model=List[StationResponse])
def get_all_stations():
    stations = ControlledPolarTools.search_stations()
    return stations

@app.get("/api/expeditions")
def get_all_expeditions(region: str = None):
    expeditions = ControlledPolarTools.search_expeditions(region=region)
    return expeditions

@app.get("/api/datasets")
def get_datasets(station: str = None, domain: str = None):
    datasets = ControlledPolarTools.search_datasets(station_name=station, domain=domain)
    return datasets

@app.get("/api/media")
def get_media_gallery(station: str = None, category: str = None):
    media = ControlledPolarTools.search_media(station_name=station, category=category)
    return media

@app.get("/api/admin/metrics")
def get_admin_metrics():
    db: Session = SessionLocal()
    try:
        stations_count = db.query(Station).count()
        expeditions_count = db.query(Expedition).count()
        datasets_count = db.query(Dataset).count()
        media_count = db.query(MediaRecord).count()
        logs = db.query(IngestionLog).order_by(IngestionLog.started_at.desc()).limit(10).all()
        return {
            "counts": {
                "stations": stations_count,
                "expeditions": expeditions_count,
                "datasets": datasets_count,
                "media_records": media_count
            },
            "recent_logs": [
                {
                    "log_id": l.log_id,
                    "connector": l.connector_name,
                    "status": l.status,
                    "started_at": l.started_at.isoformat(),
                    "created": l.records_created,
                    "errors": l.errors_count,
                    "summary": l.summary_log
                }
                for l in logs
            ]
        }
    finally:
        db.close()
