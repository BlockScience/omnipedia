

# Omnipedia README

## Introduction

Welcome to **Omnipedia**, a sophisticated tool designed to parse and evaluate Wikipedia articles against a predefined taxonomy using advanced language models. This README provides a comprehensive explanation of the codebase, including file names, class structures (ontology), and a high-level system diagram to help you get up to speed as quickly as possible.

## Overview

Omnipedia automates the process of:

1. **Processing a Taxonomy**: Loads and processes the taxonomy to extract actionable writing requirements.
2. **Parsing Articles**: Converts Wikipedia articles into a structured format for analysis.
3. **Evaluating Articles**: Assesses articles against the extracted taxonomy requirements using a language model (OpenAI's GPT-4).
4. **Providing Feedback**: Generates scores and feedback for each section of the article based on adherence to the taxonomy.

## File Structure

The project consists of multiple Python scripts organized into components:

```
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
```

## Dependencies

The project relies on the following Python packages:

- `aiofiles`
- `litellm`
- `mwparserfromhell`
- `nltk`
- `openai`
- `logging`

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Settings and Configuration

The `config.py` file in the `utils` directory handles configuration:

- **TAXONOMY_LABELS**: Predefined labels for article sections.
- **Logging Setup**: Configures logging level and format.

## Exception Handling

Custom exceptions are defined in various components for better error management.

## Data Models (Ontology)

The code utilizes custom classes for data management. Key classes include:

```plaintext
+------------------------+
| Requirement            |
+------------------------+
| name                   |
| description            |
| applicability          |
+------------------------+

+-------------------+
| EvaluatedSentence |
+-------------------+
| sentence          |
| section           |
| title             |
| score             |
| color             |
| feedback          |
+-------------------+

+-------------+
| ArticleNode |
+-------------+
| title       |
| content     |
| section_type|
+-------------+
```

## Core Components

### 1. StyleGuideLoader

Loads the taxonomy from a JSON file.

### 2. Articulator

Parses Wikipedia articles into structured sections.

### 3. Evaluator

Evaluates parsed article sections against the taxonomy requirements.

### 4. EvaluationFunctions

Handles communication with the language model API.

### 5. Viewer

Visualizes evaluation results.

## Workflow

1. **Initialization**:

   - Load settings and initialize logging.
   - Set up the OpenAI client with the specified API key.

2. **Taxonomy Loading**:

   - Use `StyleGuideLoader` to load the taxonomy (`taxonomy.json`).

3. **Article Parsing**:

   - Use `Articulator` to parse the article (`article.txt`).
   - Generate a structured representation of the article's sections.

4. **Article Evaluation**:

   - Use `Evaluator` to evaluate each section of the article.
   - Generate scores and feedback based on adherence to the taxonomy.

5. **Output**:
   - Use `Viewer` to display the evaluation results for each section.
   - Save evaluation results to a JSON file.

## High-Level System Diagram

```plaintext
+----------------+     +--------------------+     +-----------------+
|                |     |                    |     |                 |
| taxonomy.json  | --> | StyleGuideLoader   | --> | Loaded Taxonomy |
|                |     |                    |     |                 |
+----------------+     +--------------------+     +-----------------+
                                                           |
+----------------+     +---------------+                   |
|                |     |               |                   |
| article.txt    | --> | Articulator   |                   |
|                |     |               |                   |
+----------------+     +---------------+                   |
                              |                            |
                              v                            v
                    +--------------------------------+
                    |                                |
                    |           Evaluator            |
                    | (uses EvaluationFunctions API) |
                    |                                |
                    +--------------------------------+
                              |
                              v
                    +--------------------+
                    |                    |
                    | Evaluation Results |
                    |                    |
                    +--------------------+
                              |
                              v
                    +--------------------+
                    |                    |
                    |       Viewer       |
                    |                    |
                    +--------------------+
```

## How to Run

1. **Set Up Environment**:

   - Ensure all dependencies are installed.
   - Set your OpenAI API key as an environment variable: `export OPENAI_API_KEY='your-api-key'`

2. **Prepare Files**:

   - Place your taxonomy in `taxonomy.json`.
   - Place the article to be evaluated in `article.txt`.

3. **Execute the Script**:

   ```bash
   python main.py
   ```

4. **View Results**:
   - Evaluation results will be displayed in the console.
   - Results will also be saved to `evaluation_results.json`.

## Conclusion

Omnipedia automates the evaluation of Wikipedia articles against a predefined taxonomy using advanced language models. By parsing both the taxonomy and the article, it provides detailed feedback on adherence, helping improve the quality and consistency of Wikipedia content.

---

**Note**: Ensure that the OpenAI API key is correctly set up in your environment before running the script.
