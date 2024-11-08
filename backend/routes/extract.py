from fastapi import APIRouter, HTTPException
from database.database import *
from schemas.student import Response
from prompts.extract import process_requirements
from utils.wikitext import fetch_wikitext
from pydantic import BaseModel, HttpUrl
from typing import Union


router = APIRouter()
class StyleGuideInput(BaseModel):
    content: Union[HttpUrl, str]


@router.post("/extract", response_model=Response)
async def extract_requirements(data: StyleGuideInput):
    try:
        style_guide_content = None
        # Check if the content is a string that looks like a URL
        if str(data.content).startswith(('http://', 'https://')):
            # Fetch content if URL is provided
            style_guide_content = fetch_wikitext(data.content)
        else:
            # Use the text content directly
            style_guide_content = data.content

        requirements_document = process_requirements(style_guide_content)

        # TODO: Implement function to save requirements to database
        saved_requirements = await save_requirements_to_db(requirements_document)

        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Requirements extracted and saved successfully",
            "data": saved_requirements,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def save_requirements_to_db(requirements_document):
    # Placeholder function to simulate saving requirements to the database
    # You can replace this with actual database saving logic later
    print("Saving requirements document to the database...")
    return {
        "status": "success",
        "data": {
            "message": "Placeholder for saved requirements data"
        }
    }