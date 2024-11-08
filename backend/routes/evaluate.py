from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, HttpUrl

from utils.wikitext import fetch_wikitext
from database.database import *
from schemas.student import Response
from prompts.evaluate import process_article_sections

router = APIRouter()

class EvaluateInput(BaseModel):
    text_input: Union[HttpUrl, str]
    requirements_id: str


@router.post("/evaluate", response_model=Response)
async def evaluate_text(data: EvaluateInput):
    try:
        article_content = None
        
        if str(data.text_input).startswith(('http://', 'https://')):
            article_content = fetch_wikitext(data.content)
        else:
            article_content = data.content

        requirements = await retrieve_requirements_from_db(data.requirements_id)
        evaluation_output = process_article_sections(article_content, requirements)
        saved_evaluation = await save_evaluation_to_db(evaluation_output)

        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Article evaluated successfully",
            "data": saved_evaluation,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def retrieve_requirements_from_db(requirements_guide_id: str):
    print(f"Retrieving requirements for guide ID: {requirements_guide_id}")
    return {
        "status": "success",
        "data": {
            "requirements": "Sample requirements data"
        }
    }

async def save_evaluation_to_db(evaluation_output):
    print("Saving evaluation output to the database...")
    return {
        "status": "success",
        "data": {
            "message": "Placeholder for saved evaluation data"
        }
    }