import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import Station, Expedition, Dataset, MediaRecord, Publication
from rag.vectorstore.chroma_store import PolarVectorStore
from scientific_engine.analyzer import ScientificDataAnalyzer

class ControlledPolarTools:
    @staticmethod
    def search_documents(query: str, station: Optional[str] = None, top_k: int = 4) -> List[Dict[str, Any]]:
        return PolarVectorStore.similarity_search(query=query, top_k=top_k, station_filter=station)

    @staticmethod
    def search_stations(name_or_query: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            query = db.query(Station)
            if name_or_query:
                term = f"%{name_or_query.lower()}%"
                query = query.filter(
                    (Station.name.ilike(term)) | 
                    (Station.region.ilike(term)) | 
                    (Station.location.ilike(term))
                )
            results = query.all()
            return [
                {
                    "station_id": s.station_id,
                    "name": s.name,
                    "region": s.region,
                    "location": s.location,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "commissioned_year": s.commissioned_year,
                    "status": s.operational_status,
                    "facilities": s.scientific_facilities,
                    "overview": s.overview,
                    "image_url": s.image_url
                }
                for s in results
            ]
        finally:
            db.close()

    @staticmethod
    def search_expeditions(query_term: Optional[str] = None, region: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            q = db.query(Expedition)
            if query_term:
                term = f"%{query_term.lower()}%"
                q = q.filter(
                    (Expedition.title.ilike(term)) | 
                    (Expedition.leader_name.ilike(term)) |
                    (Expedition.season_year.ilike(term)) |
                    (Expedition.key_objectives.ilike(term))
                )
            if region:
                q = q.filter(Expedition.region.ilike(f"%{region}%"))
            results = q.all()
            return [
                {
                    "expedition_id": e.expedition_id,
                    "title": e.title,
                    "region": e.region,
                    "expedition_number": e.expedition_number,
                    "season_year": e.season_year,
                    "leader": e.leader_name,
                    "vessel": e.vessel_name,
                    "departure": e.departure_date,
                    "return": e.return_date,
                    "objectives": e.key_objectives,
                    "report_url": e.summary_report_url
                }
                for e in results
            ]
        finally:
            db.close()

    @staticmethod
    def search_datasets(station_name: Optional[str] = None, domain: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            q = db.query(Dataset)
            if station_name:
                st = db.query(Station).filter(Station.name.ilike(f"%{station_name}%")).first()
                if st:
                    q = q.filter(Dataset.station_id == st.station_id)
            if domain:
                q = q.filter(Dataset.domain.ilike(f"%{domain}%"))
            if query:
                term = f"%{query.lower()}%"
                q = q.filter(Dataset.title.ilike(term))
            results = q.all()
            return [
                {
                    "dataset_id": d.dataset_id,
                    "title": d.title,
                    "domain": d.domain,
                    "station_id": d.station_id,
                    "expedition_id": d.expedition_id,
                    "time_start": d.time_start,
                    "time_end": d.time_end,
                    "temporal_resolution": d.temporal_resolution,
                    "parameters": d.parameters_measured,
                    "file_format": d.file_format,
                    "file_path": d.file_path,
                    "npdc_access_url": d.npdc_access_url,
                    "citation": d.citation,
                    "file_size_bytes": d.file_size_bytes
                }
                for d in results
            ]
        finally:
            db.close()

    @staticmethod
    def analyze_dataset(
        station: str,
        parameter: str = "temperature",
        operation: str = "mean",
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            st = db.query(Station).filter(Station.name.ilike(f"%{station}%")).first()
            if not st:
                return {"success": False, "error": f"Station '{station}' not recognized."}

            datasets = db.query(Dataset).filter(Dataset.station_id == st.station_id).all()
            if not datasets:
                return {"success": False, "error": f"No datasets indexed for station '{station}'."}

            matched_ds = None
            if year:
                for ds in datasets:
                    if str(year) in ds.title or (ds.time_start and str(year) in ds.time_start):
                        matched_ds = ds
                        break
            if not matched_ds:
                matched_ds = datasets[0]

            if not matched_ds.file_path or not pd.io.common.file_exists(matched_ds.file_path):
                return {"success": False, "error": f"Dataset file for '{matched_ds.title}' not found on disk."}

            df = pd.read_csv(matched_ds.file_path)
            res = ScientificDataAnalyzer.execute_analysis(
                df=df,
                parameter=parameter,
                operation=operation,
                year=year,
                start_date=start_date,
                end_date=end_date,
                station_name=st.name,
                dataset_title=matched_ds.title
            )
            if res.get("success"):
                res["dataset_id"] = matched_ds.dataset_id
                res["npdc_access_url"] = matched_ds.npdc_access_url
                res["citation"] = matched_ds.citation
            return res
        finally:
            db.close()

    @staticmethod
    def search_media(station_name: Optional[str] = None, category: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            q = db.query(MediaRecord)
            if station_name:
                st = db.query(Station).filter(Station.name.ilike(f"%{station_name}%")).first()
                if st:
                    q = q.filter(MediaRecord.station_id == st.station_id)
            if category:
                q = q.filter(MediaRecord.category.ilike(f"%{category}%"))
            if query:
                term = f"%{query.lower()}%"
                q = q.filter((MediaRecord.title.ilike(term)) | (MediaRecord.caption.ilike(term)))
            results = q.all()
            return [
                {
                    "media_id": m.media_id,
                    "title": m.title,
                    "category": m.category,
                    "date": m.date_captured,
                    "photographer": m.photographer,
                    "image_url": m.file_path,
                    "thumbnail_url": m.thumbnail_path,
                    "caption": m.caption,
                    "source_url": m.source_url
                }
                for m in results
            ]
        finally:
            db.close()
