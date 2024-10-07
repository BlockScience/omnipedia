# components/library/evaluation_functions.py
import re
import logging
from typing import Dict, Tuple, List
import litellm

from utils.config import ModelConfig


class EvaluationFunctions:
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config
        self.client = litellm

    async def evaluate_requirement(
        self, sentence: str, requirement: Dict
    ) -> Tuple[float, List[str]]:
        """
        Evaluates a sentence against a requirement using GPT-4.
        """
        prompt = f"""
            Evaluate the following sentence against the given requirement:

            Sentence: {sentence}
            Requirement: {requirement['Description']}

            Score the sentence from 0.0 to 1.0 based on how well it meets the requirement.
            Provide brief feedback on why the score was given.

            Response format:
            Score: [score]
            Feedback: [feedback]
            """

        try:
            response = await self.client.acompletion(
                model=self.model_config.model,
                base_url=self.model_config.base_url,
                api_key=self.model_config.api_key,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that evaluates text against requirements.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            result = response.choices[0].message.content.strip()  # type: ignore
            score_match = re.search(r"Score:\s*([0-9]*\.?[0-9]+)", result)
            feedback_match = re.search(r"Feedback:\s*(.+)", result, re.DOTALL)

            score = float(score_match[1]) if score_match else 0.0
            feedback = [feedback_match[1].strip()] if feedback_match else []

            return score, feedback
        except Exception as e:
            logging.error(f"Error during requirement evaluation: {e}")
            return 0.0, [f"Error: {str(e)}"]
