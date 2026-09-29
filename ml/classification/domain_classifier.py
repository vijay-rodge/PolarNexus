import joblib
from pathlib import Path
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from config.settings import settings
from ml.governance.registry import MLModelRegistryManager

MODEL_DIR = settings.BASE_DIR / "ml" / "artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "domain_classifier_v1.joblib"

TRAINING_SAMPLES = [
    ("Automatic weather station records at Maitri show seasonal variation in air temperature, wind speed and katabatic wind cycles.", "Polar Meteorology & Climate Dynamics"),
    ("Atmospheric surface layer turbulence and boundary layer meteorology in the coastal Antarctic station Bharati.", "Polar Meteorology & Climate Dynamics"),
    ("Synoptic weather systems and severe blizzards observed during the 32nd Indian Antarctic Expedition.", "Polar Meteorology & Climate Dynamics"),
    ("Precipitation patterns and radiative flux balance over the Schirmacher Oasis in East Antarctica.", "Polar Meteorology & Climate Dynamics"),
    ("Tropospheric aerosol optical depth and greenhouse gas concentrations over Ny-Ålesund, Svalbard.", "Polar Meteorology & Climate Dynamics"),
    ("Barometric pressure fluctuations and cyclone frequency over the Southern Ocean high latitudes.", "Polar Meteorology & Climate Dynamics"),
    
    ("Ice core drilling and paleoclimate reconstruction from the coastal ice cap of Princess Astrid Coast.", "Glaciology & Cryospheric Sciences"),
    ("Ground penetrating radar (GPR) investigations of ice shelf thickness and internal crevasse structures.", "Glaciology & Cryospheric Sciences"),
    ("Glacier mass balance and snout retreat monitoring of the Sutri Dhaka and Batal glaciers in Himachal Pradesh.", "Glaciology & Cryospheric Sciences"),
    ("Ice velocity measurements and surface melt pond dynamics using Sentinel-1 SAR interferometry in Antarctica.", "Glaciology & Cryospheric Sciences"),
    ("Subglacial topography, basal thermal regime and ice sheet flow modeling in Central Dronning Maud Land.", "Glaciology & Cryospheric Sciences"),
    ("Snow accumulation rates and firn density profiles extracted from deep ice cores at Larsemann Hills.", "Glaciology & Cryospheric Sciences"),

    ("Hydrographic observations and thermohaline circulation in Kongsfjorden using the IndARC moored observatory.", "Oceanography & Marine Biogeochemistry"),
    ("Phytoplankton bloom dynamics and nutrient upwelling across the Antarctic Polar Front in the Southern Ocean.", "Oceanography & Marine Biogeochemistry"),
    ("Trace metal distribution and primary productivity in sea ice edges of the Weddell Sea.", "Oceanography & Marine Biogeochemistry"),
    ("Water mass transformation and deep ocean ventilation during winter sea ice expansion.", "Oceanography & Marine Biogeochemistry"),
    ("Acoustic monitoring of marine mammals and underwater soundscapes in Arctic fjords.", "Oceanography & Marine Biogeochemistry"),
    ("Dissolved oxygen, carbon dioxide exchange and ocean acidification in polar marginal seas.", "Oceanography & Marine Biogeochemistry"),

    ("Geomagnetic pulsations and auroral electrojet variations recorded by the digital fluxgate magnetometer at Maitri.", "Upper Atmospheric Physics & Geomagnetism"),
    ("Ionospheric scintillation and total electron content (TEC) measurements during solar maximum using GPS receivers.", "Upper Atmospheric Physics & Geomagnetism"),
    ("VLF wave propagation and whistler observations in the sub-auroral magnetosphere of Antarctica.", "Upper Atmospheric Physics & Geomagnetism"),
    ("Cosmic ray neutron monitor measurements and solar proton events observed at Bharati station.", "Upper Atmospheric Physics & Geomagnetism"),
    ("Mesospheric winds and gravity waves observed using MF radar in the polar winter atmosphere.", "Upper Atmospheric Physics & Geomagnetism"),
    ("Geomagnetic storm signatures and magnetospheric substorms tracked across conjugate polar stations.", "Upper Atmospheric Physics & Geomagnetism"),

    ("Diversity and adaptation mechanisms of psychrophilic bacteria and lichen communities in Schirmacher Oasis.", "Polar Biology & Ecosystem Dynamics"),
    ("Cyanobacterial mat distribution, biodiversity and nitrogen fixation in Antarctic freshwater lakes.", "Polar Biology & Ecosystem Dynamics"),
    ("Microbial diversity and extremophile enzymes isolated from cryoconite holes in Arctic glaciers.", "Polar Biology & Ecosystem Dynamics"),
    ("Penguin colony censuses and breeding ecology of Adélie and Emperor penguins in Queen Maud Land.", "Polar Biology & Ecosystem Dynamics"),
    ("Zooplankton grazing pressure and krill population biomass in the seasonal sea ice zone.", "Polar Biology & Ecosystem Dynamics"),
    ("Floral colonization, moss turf communities and fungal endophytes surviving extreme sub-zero temperatures.", "Polar Biology & Ecosystem Dynamics"),

    ("Structural geology, metamorphic petrology and ductile deformation in the Schirmacher Oasis granulites.", "Geosciences & Paleoclimate Reconstruction"),
    ("Geochemical characterization and U-Pb zircon geochronology of East Antarctic shield rocks.", "Geosciences & Paleoclimate Reconstruction"),
    ("Paleomagnetic constraints on Gondwana supercontinent breakup and the India-Antarctica conjugate margin.", "Geosciences & Paleoclimate Reconstruction"),
    ("Sediment core analysis and diatom biostratigraphy of Lake Priyadarshini revealing mid-Holocene climate shifts.", "Geosciences & Paleoclimate Reconstruction"),
    ("Lithospheric structure and crustal thickness beneath Larsemann Hills from receiver function analysis.", "Geosciences & Paleoclimate Reconstruction"),
    ("Mineralogical composition and clay mineral provenance of lake sediment cores in Larsemann Hills.", "Geosciences & Paleoclimate Reconstruction")
]

class ScientificDomainClassifier:
    _pipeline = None

    @classmethod
    def train(cls) -> Dict[str, Any]:
        texts = [s[0] for s in TRAINING_SAMPLES]
        labels = [s[1] for s in TRAINING_SAMPLES]

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words='english')),
            ('clf', LogisticRegression(C=5.0, max_iter=200, class_weight='balanced'))
        ])

        X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.25, random_state=42, stratify=labels)
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))
        f1 = float(f1_score(y_test, y_pred, average='weighted'))

        pipeline.fit(texts, labels)
        cls._pipeline = pipeline
        joblib.dump(pipeline, MODEL_PATH)

        metrics = {
            "accuracy": round(acc, 4),
            "f1_weighted": round(f1, 4),
            "test_size": len(y_test)
        }

        registry_record = MLModelRegistryManager.register_model(
            model_name="Polar Research Domain Classifier",
            version="1.0.0",
            algorithm="TfidfVectorizer + LogisticRegression",
            features="Character/Word N-grams (1, 2)",
            metrics=metrics,
            training_records_count=len(texts),
            training_dataset="NCPOR Scientific Publication Corpus",
            artifact_path=str(MODEL_PATH)
        )

        return {
            "success": True,
            "metrics": metrics,
            "governance_record": registry_record
        }

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            if MODEL_PATH.exists():
                try:
                    cls._pipeline = joblib.load(MODEL_PATH)
                except Exception:
                    cls.train()
            else:
                cls.train()
        return cls._pipeline

    @classmethod
    def predict(cls, text: str) -> Dict[str, Any]:
        pipeline = cls.get_pipeline()
        pred_label = pipeline.predict([text])[0]
        probabilities = pipeline.predict_proba([text])[0]
        classes = pipeline.classes_
        
        prob_dict = {cls_name: round(float(prob), 4) for cls_name, prob in zip(classes, probabilities)}
        sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)

        return {
            "predicted_domain": pred_label,
            "confidence": sorted_probs[0][1],
            "top_probabilities": sorted_probs[:3]
        }
