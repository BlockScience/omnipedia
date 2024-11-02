import requests

import ell
import ell.lmp.tool
from fastapi import APIRouter, HTTPException
from urllib.parse import unquote

router = APIRouter()

ell.init(verbose=True, store=("./logdir"), autocommit=True)


def get_wikitext_from_url(url):
    """
    Fetches the Wikitext content of a Wikipedia page given its URL.

    Parameters:
        url (str): The full URL of the Wikipedia page.

    Returns:
        str: The Wikitext content of the page or an error message if not found.
    """
    # Validate the URL format
    if "/wiki/" not in url:
        return "Invalid Wikipedia URL format."

    # Extract and decode the page title from the URL
    title = url.split("/wiki/")[-1]
    title = unquote(title)

    # Set up the API request to get the Wikitext
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
        "format": "json",
        "formatversion": "2",
    }

    try:
        # Send the request
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Extract the Wikitext from the response
        page = data.get("query", {}).get("pages", [])[0]
        if "missing" in page:
            return "Page not found. Please check the URL."

        wikitext = page["revisions"][0]["slots"]["main"]["content"]
        return wikitext
    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching the Wikitext: {e}"
    except (KeyError, IndexError):
        return "Wikitext not found or malformed response."


@ell.simple(model="gpt-4o-mini")
def parse_website(url: str) -> str:
    """
    Converts a Wikipedia article from its URL to a comprehensive Markdown representation.

    Parameters:
        url (str): The full URL of the Wikipedia page to be converted.

    Returns:
        str: A Markdown string representing the structured content of the article.
    """
    wikitext = get_wikitext_from_url(url)

    if (
        wikitext.startswith("Invalid Wikipedia URL format")
        or wikitext.startswith("Page not found")
        or wikitext.startswith("An error occurred")
    ):
        return wikitext  # Return the error message directly

    # Define the enhanced prompt for Markdown conversion
    prompt = f"""You are an expert agent specialized in converting Wikipedia Wikitext articles into comprehensive Markdown representations. Your task is to meticulously parse the entire content, ensuring that **all elements** are captured, including but not limited to:
    
- **Title and Description:** Extract the article title and a detailed description.
- **Sections and Subsections:** Maintain the hierarchical structure of sections and subsections using appropriate Markdown syntax (e.g., `#`, `##`, `###`).
- **Templates:** Identify templates and convert them into Markdown-compatible formats or represent them as inline comments if no direct equivalent exists.
- **Guidelines and Instructions:** Capture detailed guidelines, instructions, and any procedural information with proper formatting.
- **Examples:** Extract all examples provided, ensuring they are formatted correctly (e.g., using bullet points, numbered lists, or code blocks).
- **References and Notes:** Include all references, citations, and notes, preserving their structure and links using Markdown citation styles.
- **Categories and Subcategories:** List all categories and subcategories at the end of the document, formatted appropriately.
- **Infoboxes and Tables:** Represent infoboxes and tables using Markdown table syntax, ensuring all data is accurately transcribed.
- **Formatting Elements:** Capture lists (bullet points, numbered), code snippets, images, links, and other formatting elements to preserve the original structure and intent.
- **Special Elements:** Handle any special elements such as `{{notelist}}`, `{{talkquote}}`, and other custom templates by converting them into suitable Markdown equivalents or annotating them as necessary.

The Markdown should preserve the full richness and detail of the original article without omitting any content. Here is the Wikitext content to be converted:

```
{wikitext}
```
"""
    return prompt


@router.get("/wiki")
async def parse_wiki(url: str):
    """
    Endpoint to convert a Wikipedia article URL into a comprehensive JSON representation.

    Parameters:
        url (str): The full URL of the Wikipedia page to be converted.

    Returns:
        dict: A JSON object containing the summary of the converted content or an error message.
    """
    try:
        output = parse_website(url)

        # Optionally, clean the output if the model wraps it in code blocks
        cleaned_output = output
        if output.startswith("```json") and output.endswith("```"):
            cleaned_output = output.replace("```json\n", "").replace("\n```", "")

        return {"summary": cleaned_output}
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(status_code=500, detail=str(e))
