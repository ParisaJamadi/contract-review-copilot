from typing import List, Literal

from pydantic import BaseModel, Field


class ClauseIssue(BaseModel):
    clause_name: str = Field(..., description="Short clause label")
    risk_level: Literal["low", "medium", "high"]
    issue_summary: str
    suggested_redline: str
    supporting_playbook_excerpt: str
    confidence: float = Field(..., ge=0, le=1)


class ReviewOutput(BaseModel):
    contract_type: Literal["nda", "order_form", "unknown"]
    overall_decision: Literal["approve", "approve_with_edits", "escalate"]
    overall_risk_score: int = Field(..., ge=0, le=100)
    executive_summary: str
    issues: List[ClauseIssue]
