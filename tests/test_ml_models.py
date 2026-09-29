import pytest
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from ml.classification.domain_classifier import ScientificDomainClassifier
from ml.clustering.topic_clusterer import ResearchTopicClusterer
from ml.governance.registry import MLModelRegistryManager

def test_ml_domain_classifier_training_and_prediction():
    res = ScientificDomainClassifier.train()
    assert res["success"] is True
    assert "metrics" in res
    assert "governance_record" in res

    sample_text = "Automatic weather station records continuous katabatic wind speeds and barometric pressure drops."
    pred = ScientificDomainClassifier.predict(sample_text)
    assert pred["predicted_domain"] == "Polar Meteorology & Climate Dynamics"
    assert pred["confidence"] > 0.0

def test_ml_governance_registry_persistence():
    latest = MLModelRegistryManager.get_latest_model("Polar Research Domain Classifier")
    assert latest is not None
    assert latest["version"] == "1.0.0"
    assert "metrics" in latest
    assert latest["status"] == "Production"

def test_topic_clustering():
    sample_texts = [
        "Katabatic wind speeds and atmospheric boundary layer measurements at Maitri.",
        "Ice shelf crevasse detection and ice core drilling in Dronning Maud Land.",
        "Phytoplankton bloom dynamics and nutrient upwelling across the polar front.",
        "Geomagnetic pulsations and auroral electrojet variations at Bharati."
    ]
    cluster_res = ResearchTopicClusterer.cluster_texts(sample_texts, n_clusters=2)
    assert cluster_res["n_clusters"] == 2
    assert "Cluster_1" in cluster_res["clusters"]
    assert "Cluster_2" in cluster_res["clusters"]
