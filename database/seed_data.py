import json
from pathlib import Path
from sqlalchemy.orm import Session
from database.connection import SessionLocal, Base, engine
from database.models import Station, Expedition, Dataset, Publication, MediaRecord

root_dir = Path(__file__).resolve().parent.parent

def seed_database():
    """Initializes and seeds database tables with standard polar program records."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Station).count() > 0:
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding polar research stations...")
        stations = [
            Station(
                station_id="STAT-001",
                name="Maitri",
                region="Schirmacher Oasis, Queen Maud Land, Antarctica",
                location="Schirmacher Oasis",
                latitude=-70.7661,
                longitude=11.7322,
                commissioned_year=1989,
                operational_status="Active",
                scientific_facilities=["AWS (Meteorology)", "Geomagnetic Observatory", "Seismological Station", "Priyadarshini Lake Biology Lab"],
                overview="India's second permanent Antarctic research station, commissioned in 1989. Located in the ice-free rocky Schirmacher Oasis adjacent to Lake Priyadarshini.",
                image_url="https://upload.wikimedia.org/wikipedia/commons/4/4b/Maitri_Station_Antarctica.jpg"
            ),
            Station(
                station_id="STAT-002",
                name="Bharati",
                region="Larsemann Hills, East Antarctica",
                location="Larsemann Hills",
                latitude=-69.4078,
                longitude=76.1872,
                commissioned_year=2012,
                operational_status="Active",
                scientific_facilities=["High-Throughput Satellite Ground Station (ISRO)", "Oceanographic Mooring Lab", "Atmospheric Chemistry Lab"],
                overview="Commissioned in 2012, Bharati is India's third Antarctic base featuring state-of-the-art containerized architecture on stilts with continuous real-time satellite data relay.",
                image_url="https://upload.wikimedia.org/wikipedia/commons/e/e0/Bharati_Station_Antarctica.jpg"
            ),
            Station(
                station_id="STAT-003",
                name="Dakshin Gangotri",
                region="Princess Astrid Coast, Queen Maud Land, Antarctica",
                location="Antarctic Ice Shelf",
                latitude=-70.7536,
                longitude=11.6371,
                commissioned_year=1983,
                decommissioned_year=1990,
                operational_status="Decommissioned",
                scientific_facilities=["Automatic Weather Station", "Ice Core Laboratory", "Radio Communication Shack"],
                overview="India's historic first permanent base in Antarctica, established during the 3rd Indian Expedition (1983). Decommissioned after being buried by drifting snow, preserved as a historic site.",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Dakshin_Gangotri_Post_Office.jpg/640px-Dakshin_Gangotri_Post_Office.jpg"
            ),
            Station(
                station_id="STAT-004",
                name="Himadri",
                region="Ny-Ålesund, Spitsbergen, Svalbard, Arctic",
                location="Ny-Ålesund",
                latitude=78.9167,
                longitude=11.9333,
                commissioned_year=2008,
                operational_status="Active",
                scientific_facilities=["Aerosol Chemistry Lab", "Atmospheric Boundary Layer Lab", "Glaciological Observatory"],
                overview="India's first Arctic research station opened in July 2008 at the international research base in Ny-Ålesund, Svalbard, Norway.",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Ny-%C3%85lesund_Himadri.jpg/640px-Ny-%C3%85lesund_Himadri.jpg"
            ),
            Station(
                station_id="STAT-005",
                name="IndARC",
                region="Kongsfjorden Fjord, Svalbard, Arctic",
                location="Kongsfjorden Fjord (192m depth)",
                latitude=78.9833,
                longitude=11.8167,
                commissioned_year=2014,
                operational_status="Active",
                scientific_facilities=["Moored Acoustic Doppler Current Profiler (ADCP)", "CTD Sensors", "Marine Biogeochemistry Array"],
                overview="India's first underwater moored observatory deployed at 192 meters in Kongsfjorden to monitor Arctic water mass exchanges and climate dynamics year-round.",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Kongsfjorden_Ny-Alesund.jpg/640px-Kongsfjorden_Ny-Alesund.jpg"
            ),
            Station(
                station_id="STAT-006",
                name="Himansh",
                region="Chandra Basin, Lahaul-Spiti, Western Himalayas",
                location="Sutri Dhaka (4,050m altitude)",
                latitude=32.4000,
                longitude=77.6167,
                commissioned_year=2016,
                operational_status="Active",
                scientific_facilities=["Cryosphere Meteorological Tower", "Ice Core Drill Rig", "Discharge Gauge"],
                overview="High-altitude cryospheric research station established by NCPOR in the Himalayas for glacier monitoring.",
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Himalayas_Spiti.jpg/640px-Himalayas_Spiti.jpg"
            )
        ]
        db.add_all(stations)
        db.commit()
        print(f"Successfully seeded {len(stations)} stations.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
