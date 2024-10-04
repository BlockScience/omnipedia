# components/style_guides/requirements_processor.py
from typing import Dict

def get_requirements_for_section(taxonomy: Dict, section_type: str) -> Dict:
    """
    Retrieves requirements from taxonomy for a given section type.
    """
    return taxonomy.get('ArticleComponents', {}).get(section_type, {}).get('Requirements', {})
