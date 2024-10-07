# components/storage/evaluation_results.py
import json
import logging
from pathlib import Path
from typing import Dict


class EvaluationResultsStorage:
    def __init__(self):
        self.results: Dict = {}

    def store_results(self, results: Dict):
        self.results = results

    def get_results(self) -> Dict:
        return self.results

    def save_to_file(self, output_file: str | Path):
        try:
            with open(output_file, "w") as f:
                json.dump(self.results, f, indent=2)
            logging.info(f"Evaluation results saved to {output_file}")
        except Exception as e:
            logging.error(f"Error saving evaluation results: {e}")
