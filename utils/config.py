# utils/config.py
import logging

from dataclasses import dataclass


@dataclass
class ModelConfig:
    model_id: str
    base_url: str | None = None
    api_key: str | None = None
    provider: str = "openai"

    @property
    def model(self):
        if self.provider is not None:
            return f"{self.provider}/{self.model_id}"
        return self.model_id


# Taxonomy Labels
TAXONOMY_LABELS = [
    "LeadSection",
    "GeneSection",
    "ProteinSection",
    "SpeciesTissueSubcellularDistribution",
    "FunctionSection",
    "InteractionsSection",
    "ClinicalSignificanceSection",
    "HistoryDiscoverySection",
    "Infoboxes",
    "ImagesAndDiagrams",
    "References",
    "NavigationBoxes",
    "Categories",
]

# Logging Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
