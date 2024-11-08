import ell
from typing import List

@ell.simple(model="gpt-4", temperature=0.0)
def preprocess_text(text: str) -> str:
    """Preprocess any text input to prepare it for requirement extraction."""
    return [
        ell.user(f"""Process this text to prepare it for requirement extraction. Follow these steps:

1. Identify and preserve section headers and structure
2. Clean up any markup or formatting while preserving the actual content
3. Standardize lists and bullet points
4. Remove redundant whitespace and formatting
5. Organize content into clear, logical sections if not already structured
6. Preserve any requirements-related language (must, should, will, etc.)
7. Keep any technical terms, references, or important citations

Input Text:
{text}

Return only the processed text without any additional commentary.""")
    ]