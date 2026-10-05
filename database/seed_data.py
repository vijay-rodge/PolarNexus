import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session, sessionmaker
from database.connection import SessionLocal, Base, engine as default_engine
from database.models import (
    Station,
    Expedition,
    ResearchProject,
    Dataset,
    DatasetQualityMetric,
    Publication,
    MediaRecord,
    IngestionLog,
    MLModelRegistry,
    User
)

logger = logging.getLogger(__name__)
root_dir = Path(__file__).resolve().parent.parent

# ==============================================================================
# Authentic NCPOR Polar Science Core Reference Data (SIH Problem Statement 26063)
# ==============================================================================

STATIONS_DATA = [
    {
        "station_id": "STAT-001",
        "name": "Maitri",
        "region": "Antarctica",
        "location": "Schirmacher Oasis, Queen Maud Land",
        "latitude": -70.7667,
        "longitude": 11.7333,
        "commissioned_year": 1989,
        "decommissioned_year": None,
        "operational_status": "Active (Year-Round)",
        "scientific_facilities": [
            "Meteorological Observatory",
            "Lake Priyadarshini water lab",
            "Geomagnetism station",
            "Atmospheric physics lab"
        ],
        "overview": "Maitri is India's second permanent Antarctic research station, commissioned in 1989. Located in the ice-free rocky Schirmacher Oasis adjacent to Lake Priyadarshini.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Maitri_Station_Antarctica.jpg"
    },
    {
        "station_id": "STAT-002",
        "name": "Bharati",
        "region": "Antarctica",
        "location": "Larsemann Hills",
        "latitude": -69.4072,
        "longitude": 76.1958,
        "commissioned_year": 2012,
        "decommissioned_year": None,
        "operational_status": "Active (Year-Round)",
        "scientific_facilities": [
            "State-of-the-art green research facility",
            "Remote sensing antenna",
            "Oceanographic monitoring",
            "Atmospheric observatory"
        ],
        "overview": "Commissioned in 2012, Bharati is India's third Antarctic base featuring state-of-the-art containerized architecture on stilts with continuous real-time satellite data relay.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Bharati_Station_Antarctica.jpg"
    },
    {
        "station_id": "STAT-003",
        "name": "Dakshin Gangotri",
        "region": "Antarctica",
        "location": "Princess Astrid Coast",
        "latitude": -70.0833,
        "longitude": 12.0,
        "commissioned_year": 1983,
        "decommissioned_year": 1990,
        "operational_status": "Decommissioned (Preserved as Historic Site & Transshipment Base)",
        "scientific_facilities": [
            "First permanent Indian Antarctic base",
            "Submerged in ice pack in 1989",
            "Automatic Weather Station",
            "Radio Communication Shack"
        ],
        "overview": "India's historic first permanent base in Antarctica, established during the 3rd Indian Expedition (1983). Decommissioned after being buried by drifting snow, preserved as a historic site.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Dakshin_Gangotri_Post_Office.jpg/640px-Dakshin_Gangotri_Post_Office.jpg"
    },
    {
        "station_id": "STAT-004",
        "name": "Himadri",
        "region": "Arctic",
        "location": "Ny-Ålesund, Spitsbergen, Svalbard, Norway",
        "latitude": 78.9236,
        "longitude": 11.9222,
        "commissioned_year": 2008,
        "decommissioned_year": None,
        "operational_status": "Active (Seasonal / Research Missions)",
        "scientific_facilities": [
            "Atmospheric aerosol lab",
            "Cryosphere & fjord water sampling",
            "Marine biology laboratory"
        ],
        "overview": "India's first Arctic research station opened in July 2008 at the international research base in Ny-Ålesund, Svalbard, Norway.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Ny-%C3%85lesund_Himadri.jpg/640px-Ny-%C3%85lesund_Himadri.jpg"
    },
    {
        "station_id": "STAT-005",
        "name": "IndARC",
        "region": "Arctic",
        "location": "Kongsfjorden Fjord, Svalbard",
        "latitude": 78.99,
        "longitude": 12.02,
        "commissioned_year": 2014,
        "decommissioned_year": None,
        "operational_status": "Active (Moored Underwater Observatory)",
        "scientific_facilities": [
            "Multi-sensor underwater acoustic & physical mooring",
            "Continuous arctic fjord thermohaline and current profiler"
        ],
        "overview": "India's first underwater moored observatory deployed at 192 meters in Kongsfjorden to monitor Arctic water mass exchanges and climate dynamics year-round.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Kongsfjorden_Ny-Alesund.jpg/640px-Kongsfjorden_Ny-Alesund.jpg"
    },
    {
        "station_id": "STAT-006",
        "name": "Himansh",
        "region": "Himalayas",
        "location": "Chandra Basin, Lahaul-Spiti, Himachal Pradesh",
        "latitude": 32.4042,
        "longitude": 77.6167,
        "commissioned_year": 2016,
        "decommissioned_year": None,
        "operational_status": "Active (High-Altitude Third Pole Station)",
        "scientific_facilities": [
            "Glacier mass balance lab",
            "Automatic weather station",
            "Hydrological gauging"
        ],
        "overview": "High-altitude cryospheric research station established by NCPOR in the Himalayas for glacier monitoring.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Himalayas_Spiti.jpg/640px-Himalayas_Spiti.jpg"
    }
]

EXPEDITIONS_DATA = [
    {
        "expedition_id": "EXP-ANT-01",
        "title": "1st Indian Scientific Expedition to Antarctica",
        "region": "Antarctica",
        "expedition_number": 1,
        "season_year": "1981-1982",
        "leader_name": "Dr. S.Z. Qasim",
        "vessel_name": "MV Polar Circle",
        "departure_date": "1981-12-06",
        "return_date": "1982-02-21",
        "key_objectives": "Establish India's inaugural scientific presence in Antarctica, conduct oceanographic transects, and survey Queen Maud Land.",
        "summary_report_url": "https://ncpor.res.in/expeditions/exp-ant-01/report.pdf",
        "status": "Completed"
    },
    {
        "expedition_id": "EXP-ARC-15",
        "title": "15th Indian Scientific Expedition to the Arctic",
        "region": "Arctic",
        "expedition_number": 15,
        "season_year": "2021-2022",
        "leader_name": "Dr. K.P. Krishnan",
        "vessel_name": "Teisten Research Launch",
        "departure_date": "2021-06-15",
        "return_date": "2021-10-10",
        "key_objectives": "Servicing IndARC moored observatory, fjord hydrography, glaciological ablation monitoring at Vestre Brøggerbreen, and black carbon aerosol characterization.",
        "summary_report_url": "https://ncpor.res.in/expeditions/exp-arc-15/report.pdf",
        "status": "Completed"
    },
    {
        "expedition_id": "EXP-ANT-31",
        "title": "31st Indian Scientific Expedition to Antarctica",
        "region": "Antarctica",
        "expedition_number": 31,
        "season_year": "2011-2012",
        "leader_name": "Dr. Rajesh Asthana",
        "vessel_name": "MV Ivan Papanin",
        "departure_date": "2011-11-20",
        "return_date": "2012-04-05",
        "key_objectives": "Commissioning Bharati Station at Larsemann Hills, continuous Maitri AWS weather monitoring, and Lake Priyadarshini water balance.",
        "summary_report_url": "https://ncpor.res.in/expeditions/exp-ant-31/report.pdf",
        "status": "Completed"
    },
    {
        "expedition_id": "EXP-ANT-32",
        "title": "32nd Indian Scientific Expedition to Antarctica",
        "region": "Antarctica",
        "expedition_number": 32,
        "season_year": "2012-2013",
        "leader_name": "Dr. Arun Chaturvedi",
        "vessel_name": "MV Ivan Papanin",
        "departure_date": "2012-11-15",
        "return_date": "2013-04-12",
        "key_objectives": "First full wintering operations at Bharati, geological mapping of Larsemann Hills granulites, and atmospheric boundary layer studies.",
        "summary_report_url": "https://ncpor.res.in/expeditions/exp-ant-32/report.pdf",
        "status": "Completed"
    },
    {
        "expedition_id": "EXP-ANT-42",
        "title": "42nd Indian Scientific Expedition to Antarctica",
        "region": "Antarctica",
        "expedition_number": 42,
        "season_year": "2022-2023",
        "leader_name": "Dr. Shailendra Saini",
        "vessel_name": "MV Vasiliy Golovnin",
        "departure_date": "2022-12-10",
        "return_date": "2023-04-02",
        "key_objectives": "Ice core drilling in coastal Dronning Maud Land, deployment of automated GNSS receivers, and replacement of Maitri fuel tanks.",
        "summary_report_url": "https://ncpor.res.in/expeditions/exp-ant-42/report.pdf",
        "status": "Completed"
    }
]

DATASETS_DATA = [
    {
        "dataset_id": "DS-AWS-MAITRI-2012",
        "title": "Maitri Automatic Weather Station (AWS) Meteorological Data 2012",
        "domain": "Polar Meteorology & Climate Dynamics",
        "station_id": "STAT-001",
        "expedition_id": "EXP-ANT-31",
        "time_start": "2012-01-01 00:00:00",
        "time_end": "2012-12-31 23:00:00",
        "temporal_resolution": "Hourly",
        "parameters_measured": ["air_temperature", "wind_speed", "atmospheric_pressure", "relative_humidity"],
        "file_format": "CSV",
        "file_path": "data/raw/aws/maitri_aws_2012.csv",
        "npdc_access_url": "https://npdc.ncpor.res.in/datasets/DS-AWS-MAITRI-2012",
        "license": "Open Access (NCPOR / MoES Policy)",
        "file_size_bytes": 446223,
        "citation": "India Meteorological Department & NCPOR (2012). Surface Meteorological Observations at Maitri Station, East Antarctica. National Polar Data Center (NPDC)."
    },
    {
        "dataset_id": "DS-AWS-MAITRI-2013",
        "title": "Maitri Automatic Weather Station (AWS) Meteorological Data 2013",
        "domain": "Polar Meteorology & Climate Dynamics",
        "station_id": "STAT-001",
        "expedition_id": "EXP-ANT-32",
        "time_start": "2013-01-01 00:00:00",
        "time_end": "2013-12-31 23:00:00",
        "temporal_resolution": "Hourly",
        "parameters_measured": ["air_temperature", "wind_speed", "atmospheric_pressure", "relative_humidity"],
        "file_format": "CSV",
        "file_path": "data/raw/aws/maitri_aws_2013.csv",
        "npdc_access_url": "https://npdc.ncpor.res.in/datasets/DS-AWS-MAITRI-2013",
        "license": "Open Access (NCPOR / MoES Policy)",
        "file_size_bytes": 445746,
        "citation": "India Meteorological Department & NCPOR (2013). Surface Meteorological Observations at Maitri Station. NPDC."
    },
    {
        "dataset_id": "DS-AWS-BHARATI-2014",
        "title": "Bharati Coastal AWS Surface Weather Observations 2014",
        "domain": "Polar Meteorology & Climate Dynamics",
        "station_id": "STAT-002",
        "expedition_id": "EXP-ANT-32",
        "time_start": "2014-01-01 00:00:00",
        "time_end": "2014-12-31 23:00:00",
        "temporal_resolution": "Hourly",
        "parameters_measured": ["air_temperature", "wind_speed", "atmospheric_pressure", "relative_humidity"],
        "file_format": "CSV",
        "file_path": "data/raw/aws/bharati_aws_2014.csv",
        "npdc_access_url": "https://npdc.ncpor.res.in/datasets/DS-AWS-BHARATI-2014",
        "license": "Open Access (NCPOR / MoES Policy)",
        "file_size_bytes": 454856,
        "citation": "NCPOR Atmospheric Sciences Division (2014). Meteorological Dataset for Bharati Station, Larsemann Hills. NPDC."
    }
]

DATASET_METRICS_DATA = [
    {
        "metric_id": "QM-DS-AWS-MAITRI-2012",
        "dataset_id": "DS-AWS-MAITRI-2012",
        "row_count": 8784,
        "column_count": 6,
        "missing_values_count": 0,
        "duplicate_rows": 0,
        "date_continuity_score": 1.0
    },
    {
        "metric_id": "QM-DS-AWS-MAITRI-2013",
        "dataset_id": "DS-AWS-MAITRI-2013",
        "row_count": 8760,
        "column_count": 6,
        "missing_values_count": 0,
        "duplicate_rows": 0,
        "date_continuity_score": 1.0
    },
    {
        "metric_id": "QM-DS-AWS-BHARATI-2014",
        "dataset_id": "DS-AWS-BHARATI-2014",
        "row_count": 8760,
        "column_count": 6,
        "missing_values_count": 0,
        "duplicate_rows": 0,
        "date_continuity_score": 1.0
    }
]

PUBLICATIONS_DATA = [
    {
        "publication_id": "PUB-2020-001",
        "title": "Decadal Trends in Surface Temperature and Katabatic Wind Regimes at Maitri Station, East Antarctica",
        "authors": "Asthana, R., Beg, M.J., & Lal, M.",
        "year": 2020,
        "journal_name": "Polar Science",
        "doi": "10.1016/j.polar.2020.100523",
        "domain": "Polar Meteorology & Climate Dynamics",
        "abstract": "We analyze three decades of continuous meteorological observations at Maitri station in the Schirmacher Oasis. Katabatic wind frequencies correlate strongly with inland ice sheet cooling and maritime low-pressure systems.",
        "keywords": ["katabatic wind", "maitri", "antarctica", "meteorology"],
        "station_id": "STAT-001",
        "expedition_id": "EXP-ANT-31",
        "dspace_handle_url": "https://dspace.ncpor.res.in/handle/1807/pub-2020-001"
    },
    {
        "publication_id": "PUB-2021-002",
        "title": "Year-Round Moored Acoustic and Thermohaline Observations in Kongsfjorden by IndARC",
        "authors": "Krishnan, K.P., Ravichandran, M., & Subeesh, M.P.",
        "year": 2021,
        "journal_name": "Journal of Marine Systems",
        "doi": "10.1016/j.jmarsys.2021.103590",
        "domain": "Oceanography & Marine Biogeochemistry",
        "abstract": "Continuous time-series from the IndARC underwater mooring reveal rhythmic pulses of warm Atlantic Water entering Kongsfjorden during late autumn, modifying fjord stratification and tidewater glacier melting rates.",
        "keywords": ["indarc", "kongsfjorden", "svalbard", "atlantic water", "oceanography"],
        "station_id": "STAT-005",
        "expedition_id": "EXP-ARC-15",
        "dspace_handle_url": "https://dspace.ncpor.res.in/handle/1807/pub-2021-002"
    },
    {
        "publication_id": "PUB-2018-003",
        "title": "Boundary Layer Meteorology and Energy Flux Exchange over Bharati Station, Larsemann Hills",
        "authors": "Srivastava, P., Patil, S., & Shailendra, S.",
        "year": 2018,
        "journal_name": "Atmospheric Research",
        "doi": "10.1016/j.atmosres.2018.06.012",
        "domain": "Polar Meteorology & Climate Dynamics",
        "abstract": "Eddy covariance observations at Bharati station show distinct seasonal variations in surface heat flux between coastal rocky terrain and adjacent fast ice cover in Prydz Bay.",
        "keywords": ["boundary layer", "bharati station", "larsemann hills", "energy flux"],
        "station_id": "STAT-002",
        "expedition_id": "EXP-ANT-32",
        "dspace_handle_url": "https://dspace.ncpor.res.in/handle/1807/pub-2018-003"
    },
    {
        "publication_id": "PUB-2022-004",
        "title": "Cryoconite Microbial Communities and Biogeochemical Cycling in Arctic Glaciers",
        "authors": "Singh, S.M., Sharma, J., & Roy, C.",
        "year": 2022,
        "journal_name": "FEMS Microbiology Ecology",
        "doi": "10.1093/femsec/fiac045",
        "domain": "Polar Biology & Ecosystem Dynamics",
        "abstract": "Isolation of cold-active psychrophilic bacteria and fungi from cryoconite holes on glaciers near Ny-Ålesund, Svalbard demonstrated novel enzymatic adaptations for carbon utilization under freezing conditions.",
        "keywords": ["cryoconite", "arctic", "microbiology", "glaciers", "svalbard"],
        "station_id": "STAT-004",
        "expedition_id": "EXP-ARC-15",
        "dspace_handle_url": "https://dspace.ncpor.res.in/handle/1807/pub-2022-004"
    },
    {
        "publication_id": "PUB-DSPACE-123456789-133",
        "title": "Position fixing in Antarctica",
        "authors": "Pathak, M.C.",
        "year": 2006,
        "journal_name": "First Indian Scientific Expedition to Antarctica: Technical Report",
        "doi": None,
        "domain": "Oceanography & Geodesy",
        "abstract": "During the First Indian Antarctic Expedition, establishing accurate geodetic benchmarks in Antarctica's ice sheet was critical. This study deployed an advanced satellite Doppler navigation system to calculate definitive coordinates for India's scientific foothold at Dakshin Gangotri.",
        "keywords": ["satellite navigation", "geodesy", "dakshin gangotri", "doppler positioning", "antarctica"],
        "station_id": "STAT-003",
        "expedition_id": "EXP-ANT-01",
        "dspace_handle_url": "http://hdl.handle.net/123456789/133"
    }
]

MEDIA_DATA = [
    {
        "media_id": "MED-001",
        "title": "Maitri Station Living Module and Priyadarshini Lake",
        "station_id": "STAT-001",
        "expedition_id": "EXP-ANT-31",
        "category": "Station Infrastructure",
        "date_captured": "2012-02-14",
        "photographer": "Dr. Rajesh Asthana",
        "file_path": "https://images.unsplash.com/photo-1517411032315-54ef2cb783bb?auto=format&fit=crop&w=1200&q=80",
        "thumbnail_path": "https://images.unsplash.com/photo-1517411032315-54ef2cb783bb?auto=format&fit=crop&w=300&q=80",
        "caption": "View of the central living and laboratory modules of Maitri Station overlooking the frozen waters of Lake Priyadarshini in Schirmacher Oasis.",
        "source_url": "https://ncpor.res.in/gallery/maitri/photo1.jpg"
    },
    {
        "media_id": "MED-002",
        "title": "Bharati Research Base Aerial Panorama, Larsemann Hills",
        "station_id": "STAT-002",
        "expedition_id": "EXP-ANT-32",
        "category": "Station Infrastructure",
        "date_captured": "2013-01-20",
        "photographer": "NCPOR Expedition Team",
        "file_path": "https://images.unsplash.com/photo-1548263594-a71ea65a8598?auto=format&fit=crop&w=1200&q=80",
        "thumbnail_path": "https://images.unsplash.com/photo-1548263594-a71ea65a8598?auto=format&fit=crop&w=300&q=80",
        "caption": "Aerodynamic stilted structure of Bharati Station at Larsemann Hills overlooking the icebergs of Prydz Bay.",
        "source_url": "https://ncpor.res.in/gallery/bharati/photo2.jpg"
    },
    {
        "media_id": "MED-003",
        "title": "Himadri Research Station, Ny-Ålesund, Svalbard",
        "station_id": "STAT-004",
        "expedition_id": "EXP-ARC-15",
        "category": "Station Infrastructure",
        "date_captured": "2021-07-12",
        "photographer": "Dr. K.P. Krishnan",
        "file_path": "https://images.unsplash.com/photo-1516431883659-655d41c09bf9?auto=format&fit=crop&w=1200&q=80",
        "thumbnail_path": "https://images.unsplash.com/photo-1516431883659-655d41c09bf9?auto=format&fit=crop&w=300&q=80",
        "caption": "Himadri, India's research headquarters in the international science village of Ny-Ålesund with snow-capped Arctic fjords in the background.",
        "source_url": "https://ncpor.res.in/gallery/himadri/photo1.jpg"
    },
    {
        "media_id": "MED-004",
        "title": "Aurora Australis Dancing over Maitri Observatory",
        "station_id": "STAT-001",
        "expedition_id": "EXP-ANT-31",
        "category": "Aurora",
        "date_captured": "2012-06-21",
        "photographer": "Indian Wintering Team",
        "file_path": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=1200&q=80",
        "thumbnail_path": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=300&q=80",
        "caption": "Brilliant green curtains of Aurora Australis illuminating the polar night sky above the geomagnetic observatory at Maitri.",
        "source_url": "https://ncpor.res.in/gallery/aurora/maitri_aurora.jpg"
    },
    {
        "media_id": "MED-005",
        "title": "Adélie Penguin Colony on Fast Ice near Bharati",
        "station_id": "STAT-002",
        "expedition_id": "EXP-ANT-32",
        "category": "Wildlife",
        "date_captured": "2013-02-10",
        "photographer": "Polar Biology Division",
        "file_path": "https://images.unsplash.com/photo-1598439210625-5067c578f3f6?auto=format&fit=crop&w=1200&q=80",
        "thumbnail_path": "https://images.unsplash.com/photo-1598439210625-5067c578f3f6?auto=format&fit=crop&w=300&q=80",
        "caption": "Curious Adélie penguins (Pygoscelis adeliae) congregating on the sea ice near Bharati Station in Larsemann Hills.",
        "source_url": "https://ncpor.res.in/gallery/wildlife/adelie_bharati.jpg"
    },
    {
        "media_id": "MED-PUB-PUB-DSPACE-123456789-133-1",
        "title": "Figure 1: Orbital geometry and polar transit trajectories",
        "station_id": "STAT-003",
        "expedition_id": "EXP-ANT-01",
        "category": "Technical Diagram & Survey Maps",
        "date_captured": "1982",
        "photographer": "M. C. Pathak / 1st Indian Antarctic Expedition",
        "file_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_1_page_1_691x320.png",
        "thumbnail_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_1_page_1_691x320.png",
        "caption": "Figure 1: Orbital geometry and polar transit trajectories of Doppler navigation satellites vis-à-vis Earth rotation.",
        "source_url": "http://hdl.handle.net/123456789/133"
    },
    {
        "media_id": "MED-PUB-PUB-DSPACE-123456789-133-2",
        "title": "Figure 2: Polar orbital constellation coverage",
        "station_id": "STAT-003",
        "expedition_id": "EXP-ANT-01",
        "category": "Technical Diagram & Survey Maps",
        "date_captured": "1982",
        "photographer": "M. C. Pathak / 1st Indian Antarctic Expedition",
        "file_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_2_page_2_498x133.png",
        "thumbnail_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_2_page_2_498x133.png",
        "caption": "Figure 2: Polar orbital constellation coverage over high-latitude Antarctic coordinates.",
        "source_url": "http://hdl.handle.net/123456789/133"
    },
    {
        "media_id": "MED-PUB-PUB-DSPACE-123456789-133-3",
        "title": "Figure 3: Survey Map showing geodetic positions fixed",
        "station_id": "STAT-003",
        "expedition_id": "EXP-ANT-01",
        "category": "Technical Diagram & Survey Maps",
        "date_captured": "1982",
        "photographer": "M. C. Pathak / 1st Indian Antarctic Expedition",
        "file_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_3_page_3_1977x2265.png",
        "thumbnail_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_3_page_3_1977x2265.png",
        "caption": "Figure 3: Survey Map showing geodetic positions fixed by Satellite Navigation during the First Indian Antarctic Expedition.",
        "source_url": "http://hdl.handle.net/123456789/133"
    },
    {
        "media_id": "MED-PUB-PUB-DSPACE-123456789-133-4",
        "title": "Figure 4 & 5: Satellite navigation receiver deployment",
        "station_id": "STAT-003",
        "expedition_id": "EXP-ANT-01",
        "category": "Technical Diagram & Survey Maps",
        "date_captured": "1982",
        "photographer": "M. C. Pathak / 1st Indian Antarctic Expedition",
        "file_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_4_page_4_948x519.png",
        "thumbnail_path": "data/raw/media/extracted_figures/123456789_133_File_Description_SizeFormat_ARTICLE_4/fig_4_page_4_948x519.png",
        "caption": "Figure 4 & 5: Satellite navigation receiver operational deployment and coordinate terminal printout at Dakshin Gangotri.",
        "source_url": "http://hdl.handle.net/123456789/133"
    }
]

INGESTION_LOGS_DATA = [
    {
        "log_id": "LOG-INIT-001",
        "connector_name": "NCPOR & NPDC Master Seeder",
        "started_at": datetime(2026, 9, 28, 18, 26, 25),
        "completed_at": datetime(2026, 9, 28, 18, 31, 25),
        "status": "SUCCESS",
        "records_discovered": 25,
        "records_created": 25,
        "records_updated": 0,
        "duplicates_count": 0,
        "errors_count": 0,
        "summary_log": "Successfully initialized core polar stations, expeditions, AWS hourly time-series, publications, and media gallery."
    },
    {
        "log_id": "LOG-DSPACE-063504",
        "connector_name": "NCPOR DSpace Live Harvester",
        "started_at": datetime(2026, 9, 29, 6, 35, 4),
        "completed_at": datetime(2026, 9, 29, 6, 35, 5),
        "status": "SUCCESS",
        "records_discovered": 1,
        "records_created": 1,
        "records_updated": 0,
        "duplicates_count": 0,
        "errors_count": 0,
        "summary_log": "Successfully harvested Position fixing in Antarctica (File Description SizeFormat ARTICLE 4.pdf) from DSpace handle 123456789/133. Indexed 8 chunks into ChromaDB."
    }
]

def seed_database(target_engine=None) -> Dict[str, int]:
    """
    Idempotently seeds database tables with standard PolarNexus records.
    Ensures all tables exist first via create_all, checks existing records by primary key,
    and inserts missing rows without overwriting or deleting any existing data.
    """
    use_engine = target_engine or default_engine
    Base.metadata.create_all(bind=use_engine, checkfirst=True)
    
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=use_engine)
    db: Session = session_factory()
    
    summary = {
        "stations_added": 0,
        "expeditions_added": 0,
        "datasets_added": 0,
        "metrics_added": 0,
        "publications_added": 0,
        "media_added": 0,
        "logs_added": 0
    }

    try:
        # 1. Seed Stations
        for item in STATIONS_DATA:
            existing = db.query(Station).filter(Station.station_id == item["station_id"]).first()
            if not existing:
                st = Station(**item)
                db.add(st)
                summary["stations_added"] += 1
        db.commit()

        # 2. Seed Expeditions
        for item in EXPEDITIONS_DATA:
            existing = db.query(Expedition).filter(Expedition.expedition_id == item["expedition_id"]).first()
            if not existing:
                exp = Expedition(**item)
                db.add(exp)
                summary["expeditions_added"] += 1
        db.commit()

        # 3. Seed Datasets
        for item in DATASETS_DATA:
            existing = db.query(Dataset).filter(Dataset.dataset_id == item["dataset_id"]).first()
            if not existing:
                ds = Dataset(**item)
                db.add(ds)
                summary["datasets_added"] += 1
        db.commit()

        # 4. Seed Dataset Quality Metrics
        for item in DATASET_METRICS_DATA:
            existing = db.query(DatasetQualityMetric).filter(DatasetQualityMetric.metric_id == item["metric_id"]).first()
            if not existing:
                qm = DatasetQualityMetric(**item)
                db.add(qm)
                summary["metrics_added"] += 1
        db.commit()

        # 5. Seed Publications
        for item in PUBLICATIONS_DATA:
            existing = db.query(Publication).filter(Publication.publication_id == item["publication_id"]).first()
            if not existing:
                pub = Publication(**item)
                db.add(pub)
                summary["publications_added"] += 1
        db.commit()

        # 6. Seed Media Records
        for item in MEDIA_DATA:
            existing = db.query(MediaRecord).filter(MediaRecord.media_id == item["media_id"]).first()
            if not existing:
                med = MediaRecord(**item)
                db.add(med)
                summary["media_added"] += 1
        db.commit()

        # 7. Seed Ingestion Logs
        for item in INGESTION_LOGS_DATA:
            existing = db.query(IngestionLog).filter(IngestionLog.log_id == item["log_id"]).first()
            if not existing:
                log_entry = IngestionLog(**item)
                db.add(log_entry)
                summary["logs_added"] += 1
        db.commit()

        logger.info(f"Database seeding completed successfully: {summary}")
        return summary

    except Exception as e:
        db.rollback()
        logger.error(f"Error during database seeding: {e}", exc_info=True)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
