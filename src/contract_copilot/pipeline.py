import json
from datetime import datetime
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .config import MODEL_NAME, OUTPUTS_DIR, RUBRIC_PATH
from .retrieval import retrieve_playbook_context
from .schemas import ReviewOutput


SYSTEM_PROMPT = """
You are an AI contract review assistant for a commercial legal team.
Your task is to review low-stakes NDAs and order forms.

Rules:
- Be conservative: escalate when uncertainty is high.
- Use playbook context as the primary reference.
- Only output valid JSON that matches the required schema.
- Keep explanations concise and business-friendly.
- Do not invent clauses, facts, or policy text.
- Every issue must be grounded in the provided contract text and playbook/rubric.
"""


def _score_from_issues(report: ReviewOutput) -> int:
    severity_points = {"low": 10, "medium": 20, "high": 35}
    score = sum(severity_points.get(issue.risk_level, 0) for issue in report.issues)
    return min(100, score)


def _decision_from_score(score: int) -> str:
    if score <= 20:
        return "approve"
    if score <= 50:
        return "approve_with_edits"
    return "escalate"


def _apply_rubric(report: ReviewOutput) -> ReviewOutput:
    score = _score_from_issues(report)
    decision = _decision_from_score(score)
    return report.model_copy(
        update={
            "overall_risk_score": score,
            "overall_decision": decision,
        }
    )


def _load_rubric_text(custom_rubric_text: str | None = None) -> str:
    if custom_rubric_text and custom_rubric_text.strip():
        return custom_rubric_text.strip()
    if RUBRIC_PATH.exists():
        return RUBRIC_PATH.read_text(encoding="utf-8")
    return "No rubric provided."


def run_review(contract_text: str, rubric_text: str | None = None) -> ReviewOutput:
    context = retrieve_playbook_context(contract_text)
    active_rubric = _load_rubric_text(rubric_text)
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
    structured_llm = llm.with_structured_output(ReviewOutput)

    user_prompt = f"""
Review the contract text below and produce the structured output.
Use the rubric and playbook as strict policy guidance.
If an issue is not supported by contract/playbook evidence, do not include it.

Contract text:
{contract_text}

Relevant playbook context:
{context}

Rubric:
{active_rubric}
"""
    raw_result = structured_llm.invoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_prompt)]
    )
    return _apply_rubric(raw_result)


def save_report(report: ReviewOutput, output_dir: Path | None = None) -> Path:
    output_dir = output_dir or OUTPUTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"review_report_{ts}.json"
    out_path.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
    return out_path
