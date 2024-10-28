from pydantic import BaseModel
from typing import List


class RequirementEvaluation(BaseModel):
    requirement_id: str
    applicable: bool
    applicability_reasoning: str
    score: float
    confidence: float
    evidence: str
    reasoning: str
    overlap_notes: str


class SectionEvaluation(BaseModel):
    title: str
    requirement_evaluations: List[RequirementEvaluation]
    meta_notes: str


class EvaluationOutput(BaseModel):
    sections: List[SectionEvaluation]

    class Config:
        json_schema_extra = {
            "example": {
                "sections": [
                    {
                        "title": "Overview",
                        "requirement_evaluations": [
                            {
                                "requirement_id": "R2",
                                "applicable": True,
                                "applicability_reasoning": "Relevant because the Overview focuses on gene/protein function, not study authors.",
                                "score": 1.0,
                                "confidence": 0.95,
                                "evidence": "The Overview discusses the ABCC11 gene and its protein, without mentioning study authors.",
                                "reasoning": "The section fully adheres to focusing on gene/protein rather than study authors.",
                                "overlap_notes": "No significant overlaps detected.",
                            },
                            {
                                "requirement_id": "R7",
                                "applicable": True,
                                "applicability_reasoning": "The section mentions gene symbols, which should be in italic as per nomenclature guidelines.",
                                "score": 0.0,
                                "confidence": 0.9,
                                "evidence": "The gene symbol 'ABCC11' is used but not written in italic font.",
                                "reasoning": "Gene symbols should be italicized per R7, which is not done here.",
                                "overlap_notes": "No significant overlaps detected.",
                            },
                        ],
                        "meta_notes": "The Overview section effectively focuses on the gene and protein, adhering to most naming and citation guidelines. However, it lacks the italicization of gene symbols and could benefit from more densely placed inline citations to fully comply with the style guide.",
                    }
                ]
            }
        }
