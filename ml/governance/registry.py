import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from config.settings import settings

REGISTRY_FILE = settings.METADATA_DIR / "ml_model_governance.json"

class MLModelRegistryManager:
    @classmethod
    def load_registry(cls) -> List[Dict[str, Any]]:
        if REGISTRY_FILE.exists():
            try:
                with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    @classmethod
    def register_model(
        cls,
        model_name: str,
        version: str,
        algorithm: str,
        features: str,
        metrics: Dict[str, float],
        training_records_count: int,
        training_dataset: str,
        artifact_path: str
    ) -> Dict[str, Any]:
        registry = cls.load_registry()
        record = {
            "model_id": f"MOD-{model_name.lower().replace(' ', '_')}-{version}",
            "model_name": model_name,
            "version": version,
            "algorithm": algorithm,
            "features": features,
            "metrics": metrics,
            "training_records_count": training_records_count,
            "training_dataset": training_dataset,
            "artifact_path": str(artifact_path),
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "Production"
        }
        existing_idx = next((i for i, m in enumerate(registry) if m["model_name"] == model_name and m["version"] == version), None)
        if existing_idx is not None:
            registry[existing_idx] = record
        else:
            registry.append(record)

        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        return record

    @classmethod
    def get_latest_model(cls, model_name: str) -> Optional[Dict[str, Any]]:
        registry = cls.load_registry()
        matching = [m for m in registry if m["model_name"] == model_name]
        return matching[-1] if matching else None
