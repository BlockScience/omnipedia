import asyncio
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

from components.style_guides.style_guide_loader import load_taxonomy
from components.style_guides.requirements_processor import get_requirements_for_section
from components.library.text_processing import split_into_sentences, split_custom_references
from components.library.evaluation_functions import EvaluationFunctions
from components.articulator.articulator import Articulator
from components.evaluator.evaluator import Evaluator, WikipediaClassifier
from components.storage.decomposed_content import DecomposedContentStorage
from components.storage.evaluation_results import EvaluationResultsStorage
from components.viewer_editor.viewer import Viewer
from utils.config import TAXONOMY_LABELS

import aiofiles

async def process_single_file(file_path):
    # Load taxonomy
    taxonomy_file = 'taxonomy.json'
    try:
        taxonomy = load_taxonomy(taxonomy_file)
    except Exception as e:
        logging.error(f"Failed to load taxonomy: {e}")
        return

    # Read the article text
    try:
        async with aiofiles.open(file_path, 'r') as file:
            article = await file.read()
    except FileNotFoundError:
        logging.error(f"Article file '{file_path}' not found.")
        return

    # Initialize the evaluation functions with your OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
        return
    evaluation_functions = EvaluationFunctions(api_key)

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
    results_folder = Path('evaluation_results')
    results_folder.mkdir(exist_ok=True)

    # Store evaluation results
    results_storage = EvaluationResultsStorage()
    results_storage.store_results(processed_results)
    output_file = results_folder / f'evaluation_{Path(file_path).stem}.json'
    results_storage.save_to_file(output_file)

    logging.info(f"Processed file: {file_path}")

async def process_folder(folder_path):
    tasks = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.md'):  # Assuming all article files have .txt extension
            file_path = os.path.join(folder_path, file_name)
            tasks.append(process_single_file(file_path))
    
    await asyncio.gather(*tasks)

async def main():
    load_dotenv(verbose=True)
    
    folder_path = 'wikicrow'
    await process_folder(folder_path)

if __name__ == "__main__":
    asyncio.run(main())
