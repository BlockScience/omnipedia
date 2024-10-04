# utils/config.py
import logging

# Taxonomy Labels
TAXONOMY_LABELS = [
    'LeadSection',
    'GeneSection',
    'ProteinSection',
    'SpeciesTissueSubcellularDistribution',
    'FunctionSection',
    'InteractionsSection',
    'ClinicalSignificanceSection',
    'HistoryDiscoverySection',
    'Infoboxes',
    'ImagesAndDiagrams',
    'References',
    'NavigationBoxes',
    'Categories'
]

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
