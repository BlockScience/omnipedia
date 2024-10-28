import json
from typing import Dict, Any


def compare_evaluations(eval1: Dict[str, Any], eval2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two evaluation JSON objects and return a comparison of their scores.

    Args:
    eval1 (Dict[str, Any]): First evaluation JSON object
    eval2 (Dict[str, Any]): Second evaluation JSON object

    Returns:
    Dict[str, Any]: A dictionary containing the score comparisons
    """
    comparison = {}

    for section1, section2 in zip(eval1["sections"], eval2["sections"]):
        section_name = section1["title"]
        comparison[section_name] = {}

        for eval1, eval2 in zip(
            section1["requirement_evaluations"], section2["requirement_evaluations"]
        ):
            req_id = eval1["requirement_id"]
            score1 = eval1["score"]
            score2 = eval2["score"]

            comparison[section_name][req_id] = {
                "score1": score1,
                "score2": score2,
                "difference": abs(score2 - score1),
            }

    return comparison


# Example usage:
if __name__ == "__main__":
    # Load the JSON files
    with open("prompts/multi-wikipedia.json", "r") as f1, open(
        "prompts/multi-wikicrow.json", "r"
    ) as f2:
        eval1 = json.load(f1)
        eval2 = json.load(f2)

    # Compare the evaluations
    result = compare_evaluations(eval1, eval2)

    # Print the results
    print(json.dumps(result, indent=2))
