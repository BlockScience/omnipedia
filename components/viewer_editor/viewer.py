# components/viewer_editor/viewer.py
from typing import Dict


class Viewer:
    def visualize_evaluation(self, evaluation_results: Dict):
        """
        Visualizes evaluation results by printing color-coded sentences.
        """
        for section, sentences in evaluation_results.items():
            print(f"\n== {section} ==")
            for sentence in sentences:
                score = sentence["score"]
                if score >= 0.9:
                    color = "\033[92m"  # Green
                elif 0.7 <= score < 0.9:
                    color = "\033[93m"  # Yellow
                else:
                    color = "\033[91m"  # Red
                reset = "\033[0m"
                print(f"{color}{sentence['text']}{reset}")
                for req in sentence["requirements"]:
                    if req["score"] < 1.0:
                        print(
                            f"    Feedback ({req['requirement']}): {', '.join(req['feedback'])}"
                        )
