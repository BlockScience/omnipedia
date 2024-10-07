import asyncio
import logging
import os
from pathlib import Path

import aiofiles
from dotenv import load_dotenv

from components.articulator.articulator import Articulator
from components.evaluator.evaluator import Evaluator, WikipediaClassifier
from components.library.evaluation_functions import EvaluationFunctions
from components.storage.decomposed_content import DecomposedContentStorage
from components.storage.evaluation_results import EvaluationResultsStorage
from components.style_guides.style_guide_loader import load_taxonomy
from utils.config import ModelConfig


async def process_single_file(file_path):
    # Load taxonomy
    taxonomy_file = "taxonomy.json"
    try:
        taxonomy = load_taxonomy(taxonomy_file)
    except Exception as e:
        logging.error(f"Failed to load taxonomy: {e}")
        return

    # Read the article text
    try:
        async with aiofiles.open(file_path, "r") as file:
            article = await file.read()
    except FileNotFoundError:
        logging.error(f"Article file '{file_path}' not found.")
        return

    # Initialize the evaluation functions with your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error(
            "OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable."
        )
        return

    model_config = ModelConfig(
        model_id="gpt-4o",
        api_key=api_key,
    )
    evaluation_functions = EvaluationFunctions(model_config)

    # Initialize the classifier
    classifier = WikipediaClassifier(evaluation_functions)

    # Initialize the articulator
    articulator = Articulator(classifier)

    # Parse and decompose the article
    sections = await articulator.parse_wikipedia_sections_async(article)

    # Store decomposed content
    decomposed_storage = DecomposedContentStorage()
    decomposed_storage.store_content(sections)

    # Initialize the evaluator
    evaluator = Evaluator(evaluation_functions, taxonomy)
    evaluation_results = await evaluator.evaluate_article_sections(sections)

    # Process evaluation for frontend
    processed_results = evaluator.process_evaluation(evaluation_results)

    # Create a folder for evaluation results if it doesn't exist
    results_folder = Path("evaluation_results")
    results_folder.mkdir(exist_ok=True)

    # Store evaluation results
    results_storage = EvaluationResultsStorage()
    results_storage.store_results(processed_results)
    output_file = results_folder / f"evaluation_{Path(file_path).stem}.json"
    results_storage.save_to_file(output_file)

    logging.info(f"Processed file: {file_path}")


def batched(tasks, batch_size):
    for i in range(0, len(tasks), batch_size):
        yield tasks[i : i + batch_size]


async def process_folder(folder_path, batch_size: int = 4):
    tasks = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".md"):  # Assuming all article files have .txt extension
            file_path = os.path.join(folder_path, file_name)
            tasks.append(process_single_file(file_path))

    out = []
    for batch in batched(tasks, batch_size):
        out.extend(await asyncio.gather(*batch))
    return out


async def main():
    load_dotenv(verbose=True)

    folder_path = "wikicrow"
    await process_folder(folder_path)


if __name__ == "__main__":
    asyncio.run(main())
