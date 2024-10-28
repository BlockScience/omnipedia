from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any, List, Dict


class Requirement(BaseModel):
    id: str = Field(..., description="Unique identifier in the format 'R{id}'")
    description: str = Field(..., description="Brief description of the requirement")
    reference: str = Field(..., description="Exact quote from the style guide")
    category: str = Field(..., description="Requirement type")
    classification: str = Field(..., description="Classification of the requirement")
    where: str = Field(..., description="Where the requirement should be applied")
    when: str = Field(..., description="When the requirement should be applied")


class Group(BaseModel):
    description: str = Field(..., description="Description of the group")
    requirements: List[Requirement] = Field(default_factory=list)


class RequirementsDocument(BaseModel):
    groups: Dict[str, Group] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "groups": {
                    "General considerations": {
                        "description": "General considerations for gene and protein articles.",
                        "requirements": [
                            {
                                "id": "R1",
                                "description": "Do not hype a study by listing the authors' qualifications.",
                                "reference": 'do not hype a study by listing the names, credentials, institutions, or other "qualifications" of their authors.',
                                "category": "Content",
                                "classification": "Do not",
                                "where": "Article prose",
                                "when": "Always",
                            }
                        ],
                    }
                }
            }
        }


class RequirementEvaluation(BaseModel):
    requirement_id: str
    applicable: bool
    applicability_reasoning: Optional[str]
    score: Optional[float]
    confidence: Optional[float]
    evidence: Optional[str]
    reasoning: Optional[str]
    overlap_notes: Optional[str]


class SectionEvaluation(BaseModel):
    title: str
    requirement_evaluations: List[RequirementEvaluation]
    meta_notes: Optional[str]


class EvaluationOutput(BaseModel):
    sections: List[SectionEvaluation]

    class Config:
        json_schema_extra = {
            "example": {
                "sections": [
                    {
                        "title": "Introduction",
                        "requirement_evaluations": [
                            {
                                "requirement_id": "R1",
                                "applicable": True,
                                "applicability_reasoning": "The introduction contains information about authors.",
                                "score": 0.75,
                                "confidence": 0.9,
                                "evidence": "The introduction mentions authors but does not overly hype their qualifications.",
                                "reasoning": "The requirement is mostly met, with room for minor improvement.",
                                "overlap_notes": "No significant overlap with other sections.",
                            }
                        ],
                        "meta_notes": "The introduction is well-structured but could be improved slightly.",
                    }
                ]
            }
        }


class Response(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation successful",
                "data": "Sample data",
            }
        }
