# components/storage/decomposed_content.py
from typing import Dict, Tuple


class DecomposedContentStorage:
    def __init__(self):
        self.content: Dict[str, Tuple[str, str]] = {}

    def store_content(self, sections: Dict[str, Tuple[str, str]]):
        self.content = sections

    def get_content(self) -> Dict[str, Tuple[str, str]]:
        return self.content
