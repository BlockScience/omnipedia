#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to create directories
create_dirs() {
    echo "Creating directory structure..."

    mkdir -p components/style_guides
    mkdir -p components/articulator
    mkdir -p components/evaluator
    mkdir -p components/library
    mkdir -p components/storage
    mkdir -p components/viewer_editor
    mkdir -p utils

    echo "Directories created successfully."
}

# Function to create __init__.py files
create_init_files() {
    echo "Creating __init__.py files..."

    touch components/__init__.py
    touch components/style_guides/__init__.py
    touch components/articulator/__init__.py
    touch components/evaluator/__init__.py
    touch components/library/__init__.py
    touch components/storage/__init__.py
    touch components/viewer_editor/__init__.py
    touch utils/__init__.py

    echo "__init__.py files created."
}

# Function to create utils/config.py
create_config() {
    echo "Creating utils/config.py..."
    cat << 'EOF' > utils/config.py
# utils/config.py
import logging

# Taxonomy Labels
TAXONOMY_LABELS = [
    'LeadSection',
    'GeneSection',
    'ProteinSection',
    'SpeciesTissueSubcellularDistribution',
    'FunctionSection',
    'InteractionsSection',
    'ClinicalSignificanceSection',
    'HistoryDiscoverySection',
    'Infoboxes',
    'ImagesAndDiagrams',
    'References',
    'NavigationBoxes',
    'Categories'
]

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
EOF
    echo "utils/config.py created."
}

# Function to create components/style_guides/style_guide_loader.py
create_style_guide_loader() {
    echo "Creating components/style_guides/style_guide_loader.py..."
    cat << 'EOF' > components/style_guides/style_guide_loader.py
# components/style_guides/style_guide_loader.py
import json
import logging
from typing import Dict

def load_taxonomy(taxonomy_file_path: str) -> Dict:
    """
    Loads taxonomy from a JSON file.
    """
    try:
        with open(taxonomy_file_path, 'r') as file:
            taxonomy = json.load(file)
        return taxonomy
    except FileNotFoundError:
        logging.error(f"Taxonomy file '{taxonomy_file_path}' not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from '{taxonomy_file_path}': {e}")
        raise
EOF
    echo "components/style_guides/style_guide_loader.py created."
}

# Function to create components/style_guides/requirements_processor.py
create_requirements_processor() {
    echo "Creating components/style_guides/requirements_processor.py..."
    cat << 'EOF' > components/style_guides/requirements_processor.py
# components/style_guides/requirements_processor.py
from typing import Dict

def get_requirements_for_section(taxonomy: Dict, section_type: str) -> Dict:
    """
    Retrieves requirements from taxonomy for a given section type.
    """
    return taxonomy.get('ArticleComponents', {}).get(section_type, {}).get('Requirements', {})
EOF
    echo "components/style_guides/requirements_processor.py created."
}

# Function to create components/library/text_processing.py
create_text_processing() {
    echo "Creating components/library/text_processing.py..."
    cat << 'EOF' > components/library/text_processing.py
# components/library/text_processing.py
import re
import nltk
from typing import List

# Ensure NLTK data is downloaded
nltk.download('punkt', quiet=True)

def split_into_sentences(text: str) -> List[str]:
    """
    Splits text into sentences using NLTK's sentence tokenizer.
    """
    return nltk.sent_tokenize(text)

def split_custom_references(content: str) -> List[str]:
    """
    Custom function to split references section into proper citation blocks,
    avoiding incorrect sentence splits within structured citations.
    """
    # Regex to split references based on reference numbering in brackets
    return re.split(r'\n(?=\[\d+\. )', content.strip())
EOF
    echo "components/library/text_processing.py created."
}

# Function to create components/library/evaluation_functions.py
create_evaluation_functions() {
    echo "Creating components/library/evaluation_functions.py..."
    cat << 'EOF' > components/library/evaluation_functions.py
# components/library/evaluation_functions.py
import re
import logging
from typing import Dict, Tuple, List
import openai

class EvaluationFunctions:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def evaluate_requirement(self, sentence: str, requirement: Dict) -> Tuple[float, List[str]]:
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
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that evaluates text against requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            result = response.choices[0].message.content.strip()
            score_match = re.search(r'Score:\s*([0-9]*\.?[0-9]+)', result)
            feedback_match = re.search(r'Feedback:\s*(.+)', result, re.DOTALL)

            score = float(score_match.group(1)) if score_match else 0.0
            feedback = [feedback_match.group(1).strip()] if feedback_match else []

            return score, feedback
        except Exception as e:
            logging.error(f"Error during requirement evaluation: {e}")
            return 0.0, [f"Error: {str(e)}"]
EOF
    echo "components/library/evaluation_functions.py created."
}

# Function to create components/articulator/articulator.py
create_articulator() {
    echo "Creating components/articulator/articulator.py..."
    cat << 'EOF' > components/articulator/articulator.py
# components/articulator/articulator.py
import mwparserfromhell
import logging
from typing import Dict, Tuple
from components.library.text_processing import split_into_sentences
from components.evaluator.evaluator import WikipediaClassifier

class Articulator:
    def __init__(self, classifier: 'WikipediaClassifier'):
        self.classifier = classifier

    async def parse_wikipedia_sections_async(self, wikitext: str) -> Dict[str, Tuple[str, str]]:
        wikicode = mwparserfromhell.parse(wikitext)
        sections: Dict[str, Tuple[str, str]] = {}
        current_header = None
        current_content = []

        for node in wikicode.nodes:
            if isinstance(node, mwparserfromhell.nodes.Heading):
                if current_header is not None:
                    mapped_section = await self.classifier.gpt4_map_section_with_context(current_header, ' '.join(current_content))
                    if mapped_section not in sections:
                        sections[mapped_section] = (current_header, ' '.join(current_content))
                    else:
                        existing_title, existing_content = sections[mapped_section]
                        sections[mapped_section] = (existing_title, existing_content + ' ' + ' '.join(current_content))
                    current_content = []
                current_header = node.title.strip_code().strip()
            else:
                current_content.append(str(node).strip())

        if current_header is not None and current_content:
            mapped_section = await self.classifier.gpt4_map_section_with_context(current_header, ' '.join(current_content))
            if mapped_section not in sections:
                sections[mapped_section] = (current_header, ' '.join(current_content))
            else:
                existing_title, existing_content = sections[mapped_section]
                sections[mapped_section] = (existing_title, existing_content + ' ' + ' '.join(current_content))
        elif current_content:
            sections["LeadSection"] = ("Introduction", ' '.join(current_content))

        return sections
EOF
    echo "components/articulator/articulator.py created."
}

# Function to create components/evaluator/evaluator.py
create_evaluator() {
    echo "Creating components/evaluator/evaluator.py..."
    cat << 'EOF' > components/evaluator/evaluator.py
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
EOF
    echo "components/evaluator/evaluator.py created."
}

# Function to create components/storage/decomposed_content.py
create_decomposed_content() {
    echo "Creating components/storage/decomposed_content.py..."
    cat << 'EOF' > components/storage/decomposed_content.py
# components/storage/decomposed_content.py
from typing import Dict, Tuple

class DecomposedContentStorage:
    def __init__(self):
        self.content: Dict[str, Tuple[str, str]] = {}

    def store_content(self, sections: Dict[str, Tuple[str, str]]):
        self.content = sections

    def get_content(self) -> Dict[str, Tuple[str, str]]:
        return self.content
EOF
    echo "components/storage/decomposed_content.py created."
}

# Function to create components/storage/evaluation_results.py
create_evaluation_results() {
    echo "Creating components/storage/evaluation_results.py..."
    cat << 'EOF' > components/storage/evaluation_results.py
# components/storage/evaluation_results.py
import json
import logging
from typing import Dict

class EvaluationResultsStorage:
    def __init__(self):
        self.results: Dict = {}

    def store_results(self, results: Dict):
        self.results = results

    def get_results(self) -> Dict:
        return self.results

    def save_to_file(self, output_file: str):
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logging.info(f"Evaluation results saved to {output_file}")
        except Exception as e:
            logging.error(f"Error saving evaluation results: {e}")
EOF
    echo "components/storage/evaluation_results.py created."
}

# Function to create components/viewer_editor/viewer.py
create_viewer() {
    echo "Creating components/viewer_editor/viewer.py..."
    cat << 'EOF' > components/viewer_editor/viewer.py
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
                score = sentence['score']
                if score >= 0.9:
                    color = "\033[92m"  # Green
                elif 0.7 <= score < 0.9:
                    color = "\033[93m"  # Yellow
                else:
                    color = "\033[91m"  # Red
                reset = "\033[0m"
                print(f"{color}{sentence['text']}{reset}")
                for req in sentence['requirements']:
                    if req['score'] < 1.0:
                        print(f"    Feedback ({req['requirement']}): {', '.join(req['feedback'])}")
EOF
    echo "components/viewer_editor/viewer.py created."
}

# Function to create main.py
create_main() {
    echo "Creating main.py..."
    cat << 'EOF' > main.py
# main.py
import asyncio
import os
import logging
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

async def main():
    # Load taxonomy
    taxonomy_file = 'taxonomy.json'
    try:
        taxonomy = load_taxonomy(taxonomy_file)
    except Exception as e:
        logging.error(f"Failed to load taxonomy: {e}")
        return

    # Read the article text
    article_file = 'article.txt'
    try:
        async with aiofiles.open(article_file, 'r') as file:
            article = await file.read()
    except FileNotFoundError:
        logging.error(f"Article file '{article_file}' not found.")
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

    # Store evaluation results
    results_storage = EvaluationResultsStorage()
    results_storage.store_results(processed_results)
    results_storage.save_to_file('evaluation_results.json')

    # Visualize the evaluation
    viewer = Viewer()
    viewer.visualize_evaluation(evaluation_results)

if __name__ == "__main__":
    asyncio.run(main())
EOF
    echo "main.py created."
}

# Function to create placeholder files
create_placeholders() {
    echo "Creating placeholder files..."

    touch taxonomy.json
    touch article.txt
    touch requirements.txt

    cat << 'EOF' > README.md
# Article Evaluation System

## Overview

This project evaluates Wikipedia articles based on predefined style guides and requirements. It parses the article, evaluates each section and sentence against the requirements, and provides a visual representation of the compliance.

## Project Structure


project_root/
├── components/
│   ├── style_guides/
│   │   ├── __init__.py
│   │   ├── style_guide_loader.py
│   │   └── requirements_processor.py
│   ├── articulator/
│   │   ├── __init__.py
│   │   └── articulator.py
│   ├── evaluator/
│   │   ├── __init__.py
│   │   └── evaluator.py
│   ├── library/
│   │   ├── __init__.py
│   │   ├── text_processing.py
│   │   └── evaluation_functions.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── decomposed_content.py
│   │   └── evaluation_results.py
│   └── viewer_editor/
│       ├── __init__.py
│       └── viewer.py
├── utils/
│   ├── __init__.py
│   └── config.py
├── main.py
├── taxonomy.json
├── article.txt
├── requirements.txt
└── README.md


## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone <repository_url>
   cd project_root
   ```

2. **Set Up Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**

   Ensure you have `pip` installed. Then run:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Set your OpenAI API key:

   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

5. **Prepare Input Files:**

   - **taxonomy.json**: Define your taxonomy and requirements.
   - **article.txt**: Place the Wikipedia article text you want to evaluate.

6. **Run the Application:**

   ```bash
   python main.py
   ```

## Dependencies

- `aiofiles`
- `mwparserfromhell`
- `nltk`
- `openai`
- `logging`

Ensure all dependencies are listed in the `requirements.txt` file.

## License

[MIT License](LICENSE)

## Contact

For any questions or support, please contact [your-email@example.com](mailto:your-email@example.com).
EOF

    echo "README.md created."
}

# Function to create requirements.txt
create_requirements_txt() {
    echo "Creating requirements.txt..."
    cat << 'EOF' > requirements.txt
aiofiles
mwparserfromhell
nltk
openai
EOF
    echo "requirements.txt created."
}

# Function to display completion message
complete_message() {
    echo "Project scaffolding completed successfully!"
    echo "Next steps:"
    echo "1. Populate 'taxonomy.json' with your taxonomy and requirements."
    echo "2. Add the Wikipedia article text to 'article.txt'."
    echo "3. Install Python dependencies using 'pip install -r requirements.txt'."
    echo "4. Set your OpenAI API key as an environment variable: export OPENAI_API_KEY='your-api-key'."
    echo "5. Run the application using 'python main.py'."
}

# Execute functions
create_dirs
create_init_files
create_config
create_style_guide_loader
create_requirements_processor
create_text_processing
create_evaluation_functions
create_articulator
create_evaluator
create_decomposed_content
create_evaluation_results
create_viewer
create_main
create_placeholders
create_requirements_txt
complete_message