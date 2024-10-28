import ell
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import re


# Define data models
class RequirementEvaluation(BaseModel):
    requirement_id: str
    applicable: bool
    applicability_reasoning: Optional[str]
    score: Optional[float]
    confidence: Optional[float]
    evidence: Optional[str]
    reasoning: Optional[str]
    overlap_notes: Optional[str]


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


# Define the instructions variable
instructions = """
Your task is to establish grading criteria for each section of the article based on the given requirements. Follow the multi-step process below to ensure a thorough and accurate evaluation.

**Note**: If the content of the section is empty, there is no need to evaluate it. **Do not evaluate.**

**Initial Assessment Phase**

**Step 1: Applicability Assessment**
1. **Section-by-Section Evaluation**:
   - **Identify Applicable Requirements**:
     - For each section of the article, assess which requirements are applicable.
     - Document the reasoning for including or excluding each requirement.
   - **Document Relevance**:
     - Clearly state why each requirement is or isn't applicable.
     - Highlight any edge cases or unclear applicability.
   - **Proceed with Grading**:
     - Only grade the requirements that are applicable to the section.

**Grading Scale Definition**
- **0.0**: No adherence to the requirement.
- **0.25**: Minimal adherence with significant gaps.
- **0.5**: Partial adherence with notable room for improvement.
- **0.75**: Strong adherence with minor improvements possible.
- **1.0**: Complete adherence to the requirement.

**Evaluation Process (Per Section)**
1. **Content Mapping**:
   - **Map Requirements to Content**:
     - Link each applicable requirement to specific parts of the section's content.
   - **Identify Gaps**:
     - Note any missing or incomplete mappings.
   - **Detect Overlaps**:
     - Identify any content overlap with other sections.

2. **Detailed Evaluation**:
   - **Score Assignment**:
     - For each applicable requirement, assign a score based on the grading scale.
     - **Important**: Do not assign null to anything. The only acceptable scores are from 0.0 to 1.0.
     - If not applicable, do not grade it.
   - **Provide Evidence**:
     - Offer specific examples or evidence from the content that support the assigned score.
   - **Reasoning**:
     - Explain the rationale behind each score.
   - **Confidence Rating**:
     - Assign a confidence level (0 to 1) indicating how certain you are that the content meets the requirement.
   - **Special Considerations**:
     - Note any unique factors influencing the evaluation.

**Key Principles**
- **Applicability First**: Always assess applicability before grading.
- **Use the Full Sliding Scale**: Utilize the entire range for nuanced evaluation.
- **Specific Evidence**: Provide concrete examples for all scores.
- **Clear Reasoning**: Ensure that reasoning is transparent and easy to follow.
- **Context Awareness**: Consider the context of each section during evaluation.
- **Meaningful Overlaps**: Recognize and document significant overlaps without penalizing justified repetitions.

---

**Additional Evaluation Guidelines**

1. **Grading Scale Refinement**:
   - Emphasize the sliding nature of the grading scale to capture varying degrees of adherence.
2. **Content Complexity and Clarity**:
   - Reflect on whether the content maintains clarity and quality as per the style guide.
3. **Mapping and Observations**:
   - Map requirements to content meticulously.
   - Provide detailed observations and reasoning for each grade.
4. **Handling Overlaps and Redundancies**:
   - Assess whether overlapping information serves a meaningful purpose or is redundant.
5. **Thought Process Documentation**:
   - Document analytical processes, observations, and key details for each section.

**Output Format**

Your evaluation should be saved in the following structured JSON format:

```json
{
  "sections": [
    {
      "title": "Section Title",
      "requirement_evaluations": [
        {
          "requirement_id": "R1",
          "applicable": true,
          "applicability_reasoning": "Applicable because the lead section defines the article scope.",
          "score": 1.0,
          "confidence": 0.95,
          "evidence": "The lead starts with a clear definition of the protein.",
          "reasoning": "The section fully meets the requirement by providing a comprehensive definition.",
          "overlap_notes": "No significant overlaps detected."
        },
        {
          "requirement_id": "R7",
          "applicable": true,
          "applicability_reasoning": "Relevant to content sections to avoid redundancy.",
          "score": 0.5,
          "confidence": 0.80,
          "evidence": "Information about gene location is repeated in both infobox and content.",
          "reasoning": "Partial adherence; repetition is somewhat justified but could be streamlined.",
          "overlap_notes": "Overlap with infobox data noted."
        }
      ],
      "meta_notes": "The section is well-defined but could improve by minimizing redundant information."
    },
    {
      "title": "Another Section Title",
      "requirement_evaluations": [
        {
          "requirement_id": "R2",
          "applicable": true,
          "applicability_reasoning": "Relevant for language usage throughout the article.",
          "score": 0.75,
          "confidence": 0.90,
          "evidence": "Gene names are correctly capitalized in most instances.",
          "reasoning": "Strong adherence with minor inconsistencies in a few gene names.",
          "overlap_notes": "No overlaps in this section."
        }
      ],
      "meta_notes": "Language usage is mostly consistent, enhancing clarity and adherence to guidelines."
    }
  ]
}
```
"""


# Define the ELL function to evaluate sections iteratively
@ell.simple(model="o1-mini")
def evaluate_section(
    current_state: EvaluationOutput,
    section: Dict,
    requirements: List[Dict],
    i: int,
    total_sections: int,
):
    """Evaluate a single section of the article based on the given requirements."""
    return [
        ell.user(f"""You are an expert in evaluating article sections based on style guide requirements. Your task is to perform a detailed evaluation of the given section, following the multi-step process outlined below.

{instructions}

**Current State of Evaluation:**
{current_state.model_dump_json(indent=2)}

**Section ({i}/{total_sections}):**
{json.dumps(section, indent=2)}

**Requirements:**
{json.dumps(requirements, indent=2)}

**Remember to output only the JSON in the specified format, without any additional text.**
""")
    ]


def process_article_sections(
    sections: List[Dict], requirements: List[Dict]
) -> EvaluationOutput:
    ell.init(store="./logdir", autocommit=True, verbose=True)
    current_state = EvaluationOutput(sections=[])
    total_sections = len(sections)
    for i, section in enumerate(sections, start=1):
        # Evaluate the current section
        raw_output = evaluate_section(
            current_state, section, requirements, i, total_sections
        )
        # Clean the output (remove any potential backticks)
        json_output = raw_output.replace("```json", "").replace("```", "").strip()
        try:
            # Parse the output into an EvaluationOutput
            new_evaluation = EvaluationOutput.parse_raw(json_output)
            # Update the current state with new evaluations
            current_state.update(new_evaluation)
        except Exception as e:
            print(f"Error parsing JSON in section {i}: {e}")
            print(f"Raw output:\n{json_output}\n")
    return current_state


if __name__ == "__main__":
    # Replace with your actual sections and requirements
    with open("prompts/requirements.json") as reqs:
        requirements = json.load(reqs)
    with open("prompts/wikicrow-article.json") as article:
        sections = json.load(article)

    # Process the article sections
    evaluation_output = process_article_sections(sections, requirements)
    # Save the final JSON to a file
    with open("evaluation-wikicrow.json", "w") as outfile:
        json.dump(evaluation_output.model_dump(), outfile, indent=4)
