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
