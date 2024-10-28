import ell
from pydantic import BaseModel
from typing import List, Dict, Optional
import json


# Define data models
class RequirementEvaluation(BaseModel):
    requirement_id: str
    applicable: Optional[bool] = None
    applicability_reasoning: Optional[str] = None
    score: Optional[float] = None
    confidence: Optional[float] = None
    evidence: Optional[str] = None
    reasoning: Optional[str] = None
    overlap_notes: Optional[str] = None


class SectionEvaluation(BaseModel):
    title: str
    requirement_evaluations: List[RequirementEvaluation]
    meta_notes: Optional[str]


class EvaluationOutput(BaseModel):
    sections: List[SectionEvaluation]

    def update(self, other: "EvaluationOutput") -> "EvaluationOutput":
        """Updates the current evaluation with another, merging sections and requirement evaluations."""
        existing_section_titles = {section.title for section in self.sections}
        for section in other.sections:
            if section.title not in existing_section_titles:
                self.sections.append(section)
            else:
                # Merge requirement evaluations for the same section
                existing_section = next(
                    s for s in self.sections if s.title == section.title
                )
                existing_req_ids = {
                    req.requirement_id
                    for req in existing_section.requirement_evaluations
                }
                for req_eval in section.requirement_evaluations:
                    if req_eval.requirement_id not in existing_req_ids:
                        existing_section.requirement_evaluations.append(req_eval)
        return self


# Define the ELL function to assess applicability
@ell.simple(model="o1-mini")
def assess_applicability(
    section: Dict, requirements: List[Dict], i: int, total_sections: int
):
    """Assess which requirements are applicable to the given section."""
    return [
        ell.user(f"""You are an expert in evaluating article sections based on style guide requirements. Your task is to perform the applicability assessment for the given section.

**Instructions**:

- For the given section, assess which requirements are applicable.
- Document the reasoning for including or excluding each requirement.
- Provide the output in the following JSON format:

```json
{{
  "section_title": "{section['title']}",
  "requirement_evaluations": [
    {{
      "requirement_id": "R1",
      "applicable": true,
      "applicability_reasoning": "Reason why R1 is applicable or not applicable."
    }},
    // ... more requirements
  ]
}}
```

**Section ({i}/{total_sections})**:
{json.dumps(section, indent=2)}

**Requirements**:
{json.dumps(requirements, indent=2)}

Remember to output only the JSON in the specified format, without any additional text.
""")
    ]


# Define the ELL function to perform grading
@ell.simple(model="o1-mini")
def perform_grading(
    section: Dict,
    applicable_requirements: List[RequirementEvaluation],
    i: int,
    total_sections: int,
):
    """Perform detailed evaluation and grading of the section based on the applicable requirements."""
    applicable_requirements_json = json.dumps(
        [req.dict() for req in applicable_requirements], indent=2
    )
    return [
        ell.user(f"""You are an expert in evaluating article sections based on style guide requirements. Your task is to perform the detailed evaluation and grading for the given section.

**Instructions**:

- For each applicable requirement, assign a score based on the grading scale (0.0 to 1.0).
- Provide specific evidence, reasoning, confidence rating, and any overlap notes.
- Provide the output in the following JSON format:

```json
{{
  "section_title": "{section['title']}",
  "requirement_evaluations": [
    {{
      "requirement_id": "R1",
      "score": 1.0,
      "confidence": 0.95,
      "evidence": "Specific evidence from the content.",
      "reasoning": "Reasoning behind the score.",
      "overlap_notes": "Any overlap notes."
    }},
    // ... more requirements
  ],
  "meta_notes": "Any meta notes for the section."
}}
```

**Section ({i}/{total_sections})**:
{json.dumps(section, indent=2)}

**Applicable Requirements**:
{applicable_requirements_json}

Remember to output only the JSON in the specified format, without any additional text.
""")
    ]


# Process the article sections
def process_article_sections(
    sections: List[Dict], requirements: List[Dict]
) -> EvaluationOutput:
    ell.init(store="./logdir", autocommit=True, verbose=True)
    current_state = EvaluationOutput(sections=[])
    total_sections = len(sections)
    for i, section in enumerate(sections, start=1):
        # Step 1: Assess applicability
        raw_applicability_output = assess_applicability(
            section, requirements, i, total_sections
        )
        # Clean and parse the output
        json_output = (
            raw_applicability_output.replace("```json", "").replace("```", "").strip()
        )
        try:
            applicability_result = json.loads(json_output)
            # Extract applicable requirements
            applicable_requirements = []
            for req_eval in applicability_result["requirement_evaluations"]:
                req = RequirementEvaluation(
                    requirement_id=req_eval["requirement_id"],
                    applicable=req_eval["applicable"],
                    applicability_reasoning=req_eval.get("applicability_reasoning"),
                )
                if req.applicable:
                    applicable_requirements.append(req)
            # Step 2: Perform grading
            raw_grading_output = perform_grading(
                section, applicable_requirements, i, total_sections
            )
            json_grading_output = (
                raw_grading_output.replace("```json", "").replace("```", "").strip()
            )
            grading_result = json.loads(json_grading_output)
            # Now, merge the applicability data and grading data
            requirement_evaluations = []
            for req_eval in grading_result["requirement_evaluations"]:
                # Find the applicability reasoning
                applicability_reasoning = next(
                    (
                        req.applicability_reasoning
                        for req in applicable_requirements
                        if req.requirement_id == req_eval["requirement_id"]
                    ),
                    None,
                )
                req_eval["applicable"] = True
                req_eval["applicability_reasoning"] = applicability_reasoning
                requirement_evaluations.append(RequirementEvaluation(**req_eval))
            # Create SectionEvaluation
            section_evaluation = SectionEvaluation(
                title=section["title"],
                requirement_evaluations=requirement_evaluations,
                meta_notes=grading_result.get("meta_notes"),
            )
            # Update current_state
            current_state.sections.append(section_evaluation)
        except Exception as e:
            print(f"Error processing section {i}: {e}")
            print(f"Raw applicability output:\n{json_output}\n")
            print(f"Raw grading output:\n{json_grading_output}\n")
    return current_state


if __name__ == "__main__":
    # Replace with your actual sections and requirements
    with open("prompts/requirements.json") as reqs:
        requirements = json.load(reqs)
    with open("prompts/wikicrow-article.json") as article:
        sections = json.load(article)

    # Process the article sections
    evaluation_output = process_article_sections(sections, requirements)
    # Output the final JSON
    with open("multi-wikicrow.json", "w") as f:
        json.dump(evaluation_output.model_dump(), f, indent=4)
