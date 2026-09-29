import pytest
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scientific_engine.document_analyzer import DocumentAnalyzer

def test_benchmark_geodetic_coordinate_extraction():
    sample_ocr = """
    POLAR ORBIT (1) 108 MIN POLAR ORBIT (2)
    Position Fixing in Antarctica M. C.Pathak1
    ABSTRACT
    Antarctica with large desolate areas, snow and ice cover, few land marks, hostile weather
    and bad radio propagation conditions poses problems for position fixing. The Expedition
    used a portable land sea satellite position fixing system and least square and 3 D techniques
    to determine the following positions:
    Automatic Weather Station, Dakshin Gangotri Base Camp (Hut) Base Camp
    - 70o45' 12". 963S: 11o38' 13".618E
    - 69°59'12".672S:11°55'7".263E
    - 69°59'23".119S: H°56'26".83E
    The positions obtained were within a few metres.
    """
    coords = DocumentAnalyzer.extract_geodetic_coordinates(sample_ocr)
    assert len(coords) == 3

    # Dakshin Gangotri AWS
    aws = coords[0]
    assert aws["name"] == "Automatic Weather Station (AWS)"
    assert abs(aws["latitude"] - (-70.753601)) < 0.001
    assert abs(aws["longitude"] - 11.637116) < 0.001
    assert aws["elevation_m"] == 150.12

    # Base Camp (Hut)
    hut = coords[1]
    assert "Hut" in hut["name"]
    assert abs(hut["latitude"] - (-69.986853)) < 0.001
    assert abs(hut["longitude"] - 11.918684) < 0.001

    # Base Camp (Ice Shelf)
    shelf = coords[2]
    assert "Shelf" in shelf["name"]
    assert abs(shelf["latitude"] - (-69.989755)) < 0.001
    assert abs(shelf["longitude"] - 11.940786) < 0.001

def test_executive_summary_synthesis():
    sample_ocr = "Position Fixing in Antarctica M. C.Pathak. The Expedition used a portable satellite system."
    summary = DocumentAnalyzer.generate_executive_summary(sample_ocr, "Position Fixing in Antarctica")
    assert "Scientific Objectives" in summary
    assert "Methodology & Technology" in summary
    assert "Key Findings & Benchmark Values" in summary
    assert "Operational Implications" in summary
