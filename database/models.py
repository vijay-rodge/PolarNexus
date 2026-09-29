from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database.connection import Base

class Station(Base):
    __tablename__ = "stations"
    
    station_id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    region = Column(String(100), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    commissioned_year = Column(Integer, nullable=False)
    decommissioned_year = Column(Integer, nullable=True)
    operational_status = Column(String(50), nullable=False, default="Active")
    scientific_facilities = Column(JSON, nullable=True)
    overview = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    datasets = relationship("Dataset", back_populates="station")
    publications = relationship("Publication", back_populates="station")
    media = relationship("MediaRecord", back_populates="station")
    projects = relationship("ResearchProject", back_populates="station")

class Expedition(Base):
    __tablename__ = "expeditions"
    
    expedition_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    expedition_number = Column(Integer, nullable=True)
    season_year = Column(String(20), nullable=False, index=True)
    leader_name = Column(String(150), nullable=True)
    vessel_name = Column(String(150), nullable=True)
    departure_date = Column(String(50), nullable=True)
    return_date = Column(String(50), nullable=True)
    key_objectives = Column(Text, nullable=True)
    summary_report_url = Column(String(500), nullable=True)
    status = Column(String(50), default="Completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    datasets = relationship("Dataset", back_populates="expedition")
    publications = relationship("Publication", back_populates="expedition")
    media = relationship("MediaRecord", back_populates="expedition")
    projects = relationship("ResearchProject", back_populates="expedition")

class ResearchProject(Base):
    __tablename__ = "research_projects"
    
    project_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    domain = Column(String(150), nullable=False, index=True)
    principal_investigator = Column(String(150), nullable=True)
    institution = Column(String(255), nullable=True)
    abstract = Column(Text, nullable=True)
    station_id = Column(String(50), ForeignKey("stations.station_id"), nullable=True)
    expedition_id = Column(String(50), ForeignKey("expeditions.expedition_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    station = relationship("Station", back_populates="projects")
    expedition = relationship("Expedition", back_populates="projects")

class Dataset(Base):
    __tablename__ = "datasets"
    
    dataset_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    domain = Column(String(150), nullable=False, index=True)
    station_id = Column(String(50), ForeignKey("stations.station_id"), nullable=True)
    expedition_id = Column(String(50), ForeignKey("expeditions.expedition_id"), nullable=True)
    time_start = Column(String(50), nullable=True)
    time_end = Column(String(50), nullable=True)
    temporal_resolution = Column(String(50), nullable=True)
    parameters_measured = Column(JSON, nullable=True)
    file_format = Column(String(50), default="CSV")
    file_path = Column(String(500), nullable=True)
    npdc_access_url = Column(String(500), nullable=True)
    license = Column(String(100), default="Open Access (NCPOR / MoES Policy)")
    file_size_bytes = Column(Integer, nullable=True)
    citation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    station = relationship("Station", back_populates="datasets")
    expedition = relationship("Expedition", back_populates="datasets")
    quality_metrics = relationship("DatasetQualityMetric", back_populates="dataset", uselist=False)

class DatasetQualityMetric(Base):
    __tablename__ = "dataset_quality_metrics"
    
    metric_id = Column(String(50), primary_key=True, index=True)
    dataset_id = Column(String(50), ForeignKey("datasets.dataset_id"), nullable=False, unique=True)
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    missing_values_count = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    date_continuity_score = Column(Float, default=1.0)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="quality_metrics")

class Publication(Base):
    __tablename__ = "publications"
    
    publication_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(400), nullable=False, index=True)
    authors = Column(String(400), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    journal_name = Column(String(255), nullable=True)
    doi = Column(String(150), nullable=True)
    domain = Column(String(150), nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)
    station_id = Column(String(50), ForeignKey("stations.station_id"), nullable=True)
    expedition_id = Column(String(50), ForeignKey("expeditions.expedition_id"), nullable=True)
    dspace_handle_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    station = relationship("Station", back_populates="publications")
    expedition = relationship("Expedition", back_populates="publications")

class MediaRecord(Base):
    __tablename__ = "media_records"
    
    media_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    station_id = Column(String(50), ForeignKey("stations.station_id"), nullable=True)
    expedition_id = Column(String(50), ForeignKey("expeditions.expedition_id"), nullable=True)
    category = Column(String(100), nullable=False, index=True)
    date_captured = Column(String(50), nullable=True)
    photographer = Column(String(150), nullable=True)
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    caption = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    station = relationship("Station", back_populates="media")
    expedition = relationship("Expedition", back_populates="media")

class IngestionLog(Base):
    __tablename__ = "ingestion_logs"
    
    log_id = Column(String(50), primary_key=True, index=True)
    connector_name = Column(String(100), nullable=False, index=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)
    records_discovered = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    duplicates_count = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    summary_log = Column(Text, nullable=True)

class MLModelRegistry(Base):
    __tablename__ = "ml_model_registry"
    
    model_id = Column(String(50), primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    algorithm = Column(String(100), nullable=False)
    hyperparameters = Column(JSON, nullable=True)
    metrics_accuracy = Column(Float, nullable=True)
    metrics_f1 = Column(Float, nullable=True)
    training_records_count = Column(Integer, nullable=True)
    artifact_path = Column(String(500), nullable=True)
    trained_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="researcher")
    created_at = Column(DateTime, default=datetime.utcnow)
