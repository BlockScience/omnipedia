from fastapi import APIRouter, HTTPException

from database.database import *
from schemas.student import Response
from prompts.extract import process_requirements
from utils.wikitext import fetch_wikitext
router = APIRouter()
from pydantic import BaseModel, HttpUrl
from typing import Union

# Add this model above the router
class StyleGuideInput(BaseModel):
    content: Union[HttpUrl, str]


@router.post("/extract", response_model=Response)
async def extract_requirements(input_data: StyleGuideInput):
    try:
        style_guide_content = None
        # Check if the content is a string that looks like a URL
        if str(input_data.content).startswith(('http://', 'https://')):
            # Fetch content if URL is provided
            style_guide_content = fetch_wikitext(input_data.content)
        else:
            # Use the text content directly
            style_guide_content = input_data.content

        requirements_document = process_requirements(style_guide_content)

        # TODO: Implement function to save requirements to database
        # saved_requirements = await save_requirements_to_db(requirements_document)

        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Requirements extracted and saved successfully",
            "data": requirements_document,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

