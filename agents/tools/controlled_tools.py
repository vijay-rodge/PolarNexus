import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import or_
from sqlalchemy.orm import Session
from config.settings import settings
from database.connection import SessionLocal
from database.models import Station, Expedition, Dataset, MediaRecord, Publication
from rag.vectorstore.chroma_store import PolarVectorStore
from scientific_engine.analyzer import ScientificDataAnalyzer

logger = logging.getLogger(__name__)

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
        except Exception as e:
            logger.error(f"Error querying stations: {e}", exc_info=True)
            return []
        finally:
            db.close()

    @staticmethod
    def search_expeditions(query_term: Optional[str] = None, region: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            q = db.query(Expedition)
            results = []

            if query_term:
                term = f"%{query_term.strip().lower()}%"
                primary_q = q.filter(
                    (Expedition.title.ilike(term)) | 
                    (Expedition.leader_name.ilike(term)) |
                    (Expedition.season_year.ilike(term)) |
                    (Expedition.key_objectives.ilike(term))
                )
                if region:
                    primary_q = primary_q.filter(Expedition.region.ilike(f"%{region}%"))
                results = primary_q.all()

                # If exact phrase not matched, try specific ordinal/number matching
                if not results:
                    import re
                    ordinals = re.findall(r'\b\d+(?:st|nd|rd|th)?\b', query_term.lower())
                    if ordinals:
                        num_conditions = []
                        for ord_val in ordinals:
                            num_conditions.append(Expedition.title.ilike(f"%{ord_val}%"))
                            num_conditions.append(Expedition.key_objectives.ilike(f"%{ord_val}%"))
                        fallback_q = q.filter(or_(*num_conditions))
                        if region:
                            fallback_q = fallback_q.filter(Expedition.region.ilike(f"%{region}%"))
                        results = fallback_q.all()

                    if not results:
                        sig_words = [w for w in query_term.lower().split() if len(w) > 3 and w not in ["indian", "scientific", "expedition"]]
                        if sig_words:
                            word_conds = [Expedition.title.ilike(f"%{w}%") for w in sig_words]
                            fallback_q = q.filter(or_(*word_conds))
                            if region:
                                fallback_q = fallback_q.filter(Expedition.region.ilike(f"%{region}%"))
                            results = fallback_q.all()
            else:
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
        except Exception as e:
            logger.error(f"Error querying expeditions: {e}", exc_info=True)
            return []
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
        except Exception as e:
            logger.error(f"Error querying datasets: {e}", exc_info=True)
            return []
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

            file_path = matched_ds.file_path
            target_path = None
            if file_path:
                candidate = Path(file_path)
                if candidate.exists():
                    target_path = candidate
                else:
                    alt1 = settings.BASE_DIR / file_path.replace("\\", "/").lstrip("/")
                    alt2 = settings.RAW_DATA_DIR / "aws" / candidate.name
                    if alt1.exists():
                        target_path = alt1
                    elif alt2.exists():
                        target_path = alt2

            if not target_path or not target_path.exists():
                return {"success": False, "error": f"Dataset file for '{matched_ds.title}' not found on disk."}

            df = pd.read_csv(target_path)
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
        except Exception as e:
            logger.error(f"Error analyzing dataset: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
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
        except Exception as e:
            logger.error(f"Error querying media: {e}", exc_info=True)
            return []
        finally:
            db.close()
