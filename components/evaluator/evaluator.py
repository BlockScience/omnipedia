# components/evaluator/evaluator.py
import logging
from typing import List, Dict, Tuple
from components.library.evaluation_functions import EvaluationFunctions
from components.style_guides.requirements_processor import get_requirements_for_section
from components.library.text_processing import split_into_sentences
from utils.config import TAXONOMY_LABELS

class WikipediaClassifier:
    def __init__(self, evaluation_functions: EvaluationFunctions):
        self.evaluation_functions = evaluation_functions

    async def gpt4_map_section_with_context(self, header_text: str, section_content: str) -> str:
        """
        Uses OpenAI's GPT-4 to map a section header and its content to a taxonomy section.
        """
        prompt = f"""
            You are an assistant that maps Wikipedia article section headers to predefined taxonomy sections. 
            Given the following section header and a snippet of its content, classify it into one of the taxonomy sections: {TAXONOMY_LABELS}.

            Examples:
            Section Header: "Introduction"
            Section Content: "This section introduces the ALDOA protein, its genetic encoding, and its role in human biology."
            Mapped Taxonomy Section: LeadSection

            Section Header: "Gene Information"
            Section Content: "The ALDOA gene is located on chromosome 16 and is regulated by several transcription factors."
            Mapped Taxonomy Section: GeneSection

            Section Header: "Protein Details"
            Section Content: "ALDOA exists in multiple splice variants and undergoes post-translational modifications such as phosphorylation."
            Mapped Taxonomy Section: ProteinSection

            Section Header: "{header_text}"
            Section Content: "{section_content[:500]}..."  # Truncate to first 500 characters
            Mapped Taxonomy Section:
            """

        try:
            response = await self.evaluation_functions.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies Wikipedia sections."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            mapped_section = response.choices[0].message.content.strip()
            if mapped_section in TAXONOMY_LABELS:
                return mapped_section
            else:
                logging.warning(f"Mapped section '{mapped_section}' not in taxonomy labels.")
                return 'UncategorizedSection'
        except Exception as e:
            logging.error(f"Error during GPT-4 mapping: {e}")
            return 'UncategorizedSection'

class Evaluator:
    def __init__(self, evaluation_functions: EvaluationFunctions, taxonomy: Dict):
        self.evaluation_functions = evaluation_functions
        self.taxonomy = taxonomy

    async def evaluate_article_sections(self, sections: Dict[str, Tuple[str, str]]) -> List[Dict]:
        """
        Evaluates an article's sections against the taxonomy requirements and returns the
        evaluated sentences in a format consumable by the frontend.
        """
        evaluation_results = []

        for section_type, (section_title, content) in sections.items():
            requirements = get_requirements_for_section(self.taxonomy, section_type)
            if not requirements:
                continue

            sentences = split_into_sentences(content)

            for sentence in sentences:
                sentence_result = {
                    'sentence': sentence,
                    'section': section_type,
                    'title': section_title,  # Add the original section title
                    'score': 0.0,
                    'color': '',
                    'feedback': []
                }
                total_score = 0.0
                max_score = 0.0

                for req_name, req_details in requirements.items():
                    score, feedback = await self.evaluation_functions.evaluate_requirement(sentence, req_details)
                    sentence_result['feedback'].append({
                        'requirement': req_name,
                        'score': score,
                        'feedback': feedback
                    })

                    # Weighted scoring
                    weight = {'Mandatory': 2, 'Conditional': 1, 'Optional': 0.5}.get(req_details['Applicability'], 1)
                    total_score += score * weight
                    max_score += weight

                # Normalize the score
                normalized_score = total_score / max_score if max_score > 0 else 0.0
                sentence_result['score'] = round(normalized_score, 2)

                # Assign color based on score
                if normalized_score >= 0.9:
                    sentence_result['color'] = 'green'
                elif 0.7 <= normalized_score < 0.9:
                    sentence_result['color'] = 'yellow'
                else:
                    sentence_result['color'] = 'red'

                evaluation_results.append(sentence_result)

        return evaluation_results

    def process_evaluation(self, evaluation_results: List[Dict]) -> Dict:
        """
        Processes evaluation results to return a simplified format for frontend rendering.
        """

        frontend_data = {}

        for sentence_data in evaluation_results:
            section = sentence_data["section"]
            if section not in frontend_data:
                frontend_data[section] = []

            evaluation_summary = {
                "text": sentence_data["sentence"],
                "title": sentence_data["title"],  # Include the section title
                "score": round(sentence_data["score"], 2),
                "requirements": [
                    {
                        "requirement": req["requirement"],
                        "score": round(req["score"], 2),
                        "feedback": req["feedback"],
                    }
                    for req in sentence_data["feedback"]
                ],
                "color": self.get_color_based_on_score(sentence_data["score"]),
            }
            frontend_data[section].append(evaluation_summary)

        return frontend_data

    def get_color_based_on_score(self, score: float) -> str:
        """
        Returns a color based on the score of a sentence.
        """
        if score >= 0.9:
            return "green"
        elif score >= 0.7:
            return "yellow"
        else:
            return "red"
