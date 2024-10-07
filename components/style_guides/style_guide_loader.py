# components/style_guides/style_guide_loader.py
import json
import logging
from typing import Dict


def load_taxonomy(taxonomy_file_path: str) -> Dict:
    """
    Loads taxonomy from a JSON file.
    """
    try:
        with open(taxonomy_file_path, "r") as file:
            taxonomy = json.load(file)
        return taxonomy
    except FileNotFoundError:
        logging.error(f"Taxonomy file '{taxonomy_file_path}' not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from '{taxonomy_file_path}': {e}")
        raise
