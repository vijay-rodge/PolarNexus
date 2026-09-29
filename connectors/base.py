from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseHarvester(ABC):
    """Abstract base harvester interface for polar data repositories."""

    @abstractmethod
    def harvest_item_metadata(self, item_id: str) -> Dict[str, Any]:
        """Harvests Dublin Core / ISO metadata for a given digital repository record."""
        pass

    @abstractmethod
    def download_pdf(self, file_url: str, output_dir: str) -> Optional[str]:
        """Downloads digital bitstream to local storage."""
        pass
