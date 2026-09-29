STATIONS = {
    "MAITRI": {
        "id": "STAT-001",
        "name": "Maitri",
        "region": "Antarctica",
        "location": "Schirmacher Oasis, Queen Maud Land",
        "coordinates": {"lat": -70.7667, "lon": 11.7333},
        "commissioned": 1989,
        "status": "Active (Year-Round)",
        "facilities": ["Meteorological Observatory", "Lake Priyadarshini water lab", "Geomagnetism station", "Atmospheric physics lab"]
    },
    "BHARATI": {
        "id": "STAT-002",
        "name": "Bharati",
        "region": "Antarctica",
        "location": "Larsemann Hills",
        "coordinates": {"lat": -69.4072, "lon": 76.1958},
        "commissioned": 2012,
        "status": "Active (Year-Round)",
        "facilities": ["State-of-the-art green research facility", "Remote sensing antenna", "Oceanographic monitoring", "Atmospheric observatory"]
    },
    "DAKSHIN_GANGOTRI": {
        "id": "STAT-003",
        "name": "Dakshin Gangotri",
        "region": "Antarctica",
        "location": "Princess Astrid Coast",
        "coordinates": {"lat": -70.0833, "lon": 12.0000},
        "commissioned": 1983,
        "decommissioned": 1990,
        "status": "Decommissioned (Preserved as Historic Site & Transshipment Base)",
        "facilities": ["First permanent Indian Antarctic base", "Submerged in ice pack in 1989"]
    },
    "HIMADRI": {
        "id": "STAT-004",
        "name": "Himadri",
        "region": "Arctic",
        "location": "Ny-Ålesund, Spitsbergen, Svalbard, Norway",
        "coordinates": {"lat": 78.9236, "lon": 11.9222},
        "commissioned": 2008,
        "status": "Active (Seasonal / Research Missions)",
        "facilities": ["Atmospheric aerosol lab", "Cryosphere & fjord water sampling", "Marine biology laboratory"]
    },
    "INDARC": {
        "id": "STAT-005",
        "name": "IndARC",
        "region": "Arctic",
        "location": "Kongsfjorden Fjord, Svalbard",
        "coordinates": {"lat": 78.9900, "lon": 12.0200},
        "commissioned": 2014,
        "status": "Active (Moored Underwater Observatory)",
        "facilities": ["Multi-sensor underwater acoustic & physical mooring", "Continuous arctic fjord thermohaline and current profiler"]
    },
    "HIMANSH": {
        "id": "STAT-006",
        "name": "Himansh",
        "region": "Himalayas",
        "location": "Chandra Basin, Lahaul-Spiti, Himachal Pradesh",
        "coordinates": {"lat": 32.4042, "lon": 77.6167},
        "commissioned": 2016,
        "status": "Active (High-Altitude Third Pole Station)",
        "facilities": ["Glacier mass balance lab", "Automatic weather station", "Hydrological gauging"]
    }
}

RESEARCH_DOMAINS = [
    "Polar Meteorology & Climate Dynamics",
    "Glaciology & Cryospheric Sciences",
    "Oceanography & Marine Biogeochemistry",
    "Upper Atmospheric Physics & Geomagnetism",
    "Polar Biology & Ecosystem Dynamics",
    "Geosciences & Paleoclimate Reconstruction"
]

AWS_METEOROLOGICAL_PARAMETERS = [
    {"name": "air_temperature", "unit": "°C", "description": "Ambient air temperature at 2m"},
    {"name": "wind_speed", "unit": "m/s", "description": "Wind speed at 10m height"},
    {"name": "wind_direction", "unit": "°", "description": "Wind vector azimuth"},
    {"name": "atmospheric_pressure", "unit": "hPa", "description": "Station level barometric pressure"},
    {"name": "relative_humidity", "unit": "%", "description": "Relative air humidity"},
    {"name": "solar_radiation", "unit": "W/m²", "description": "Global downward solar irradiance"}
]

ALLOWED_SCIENTIFIC_OPERATIONS = [
    "mean", "median", "min", "max", "std", "count",
    "monthly_average", "yearly_average", "trend_slope", "anomaly"
]
