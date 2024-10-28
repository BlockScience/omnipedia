from fastapi import APIRouter, Body, HTTPException
from pydantic import HttpUrl
from typing import Dict

from database.database import *
from schemas.student import Response
from prompts.extract import process_style_guide
from prompts.evaluate import process_article_sections

router = APIRouter()


@router.post("/extract-requirements", response_model=Response)
async def extract_requirements(style_guide_url: HttpUrl = Body(...)):
    try:
        # TODO: Implement function to fetch content from URL
        style_guide_content = fetch_content_from_url(style_guide_url)

        requirements_document = process_style_guide(style_guide_content)

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


@router.post("/evaluate-article", response_model=Response)
async def evaluate_article(
    article_url: HttpUrl = Body(...), requirements_guide_id: str = Body(...)
):
    try:
        # TODO: Implement function to fetch content from URL
        article_content = fetch_content_from_url(article_url)

        # TODO: Implement function to retrieve requirements from database
        requirements = await retrieve_requirements_from_db(requirements_guide_id)

        evaluation_output = process_article_sections(article_content, requirements)

        # TODO: Implement function to save evaluation to database
        saved_evaluation = await save_evaluation_to_db(evaluation_output)

        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Article evaluated successfully",
            "data": saved_evaluation,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions (to be implemented)
def fetch_content_from_url(url: HttpUrl) -> str:
    # Implement logic to fetch content from URL
    pass


async def save_requirements_to_db(requirements_document: Dict) -> Dict:
    # Implement logic to save requirements to database
    pass


async def retrieve_requirements_from_db(guide_id: str) -> Dict:
    # Implement logic to retrieve requirements from database
    pass


async def save_evaluation_to_db(evaluation_output: Dict) -> Dict:
    # Implement logic to save evaluation to database
    pass
