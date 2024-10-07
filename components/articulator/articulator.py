# components/articulator/articulator.py
from typing import Dict, Tuple

import mwparserfromhell

from components.evaluator.evaluator import WikipediaClassifier


class Articulator:
    def __init__(self, classifier: "WikipediaClassifier"):
        self.classifier = classifier

    async def parse_wikipedia_sections_async(
        self, wikitext: str
    ) -> Dict[str, Tuple[str, str]]:
        wikicode = mwparserfromhell.parse(wikitext)
        sections: Dict[str, Tuple[str, str]] = {}
        current_header = None
        current_content = []

        for node in wikicode.nodes:
            if isinstance(node, mwparserfromhell.nodes.Heading):
                if current_header is not None:
                    mapped_section = await self.classifier.map_section_with_context(
                        current_header, " ".join(current_content)
                    )
                    print("MAPPED SECTION: ", mapped_section)
                    if mapped_section not in sections:
                        sections[mapped_section] = (
                            current_header,
                            " ".join(current_content),
                        )
                    else:
                        existing_title, existing_content = sections[mapped_section]
                        sections[mapped_section] = (
                            existing_title,
                            f"{existing_content} " + " ".join(current_content),
                        )
                    current_content = []
                current_header = node.title.strip_code().strip()
            else:
                current_content.append(str(node).strip())

        if current_header is not None and current_content:
            mapped_section = await self.classifier.map_section_with_context(
                current_header, " ".join(current_content)
            )
            if mapped_section not in sections:
                sections[mapped_section] = (current_header, " ".join(current_content))
            else:
                existing_title, existing_content = sections[mapped_section]
                sections[mapped_section] = (
                    existing_title,
                    f"{existing_content} " + " ".join(current_content),
                )
        elif current_content:
            sections["LeadSection"] = ("Introduction", " ".join(current_content))

        return sections
