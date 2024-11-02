from fastapi import APIRouter, Body, HTTPException
from pydantic import HttpUrl

from database.database import *
from schemas.student import Response
from prompts.evaluate import process_article_sections

router = APIRouter()


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
