import json
import os
import sys
from pathlib import Path

import gradio as gr

# Allow running `python ui/app.py` from project root on Windows.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.contract_copilot.config import RUBRIC_PATH
from src.contract_copilot.db import authenticate_user, create_user, init_db, log_review
from src.contract_copilot.io_utils import load_contract_text
from src.contract_copilot.pipeline import run_review, save_report


def load_default_rubric() -> str:
    if RUBRIC_PATH.exists():
        return RUBRIC_PATH.read_text(encoding="utf-8")
    return ""


def login(email: str, password: str):
    user = authenticate_user(email.strip().lower(), password)
    if not user:
        return (
            "Login failed. Check email/password.",
            None,
            gr.update(visible=True),
            gr.update(visible=False),
            "",
        )
    return (
        f"Logged in as {user['username']} ({user['role']})",
        user,
        gr.update(visible=False),
        gr.update(visible=True),
        f"Current user: {user['username']} ({user['role']})",
    )


def signup(email: str, password: str, role: str):
    ok, message = create_user(username=email, password=password, role=role)
    return message if ok else f"Sign up failed: {message}"


def logout():
    return (
        "Logged out.",
        None,
        gr.update(visible=True),
        gr.update(visible=False),
        "",
    )


def review_contract(file_obj, rubric_text, user_state):
    if not user_state:
        return "Please login first.", "", "", ""
    if file_obj is None:
        return "Please upload a contract file.", "", "", ""

    contract_text = load_contract_text(file_obj.name)
    active_rubric = rubric_text if user_state.get("role") == "legal_admin" else None
    report = run_review(contract_text, rubric_text=active_rubric)
    out_path = save_report(report)
    report_dict = report.model_dump()
    log_review(
        username=user_state["username"],
        role=user_state["role"],
        file_name=Path(file_obj.name).name,
        report_dict=report_dict,
    )

    issues_rows = []
    for issue in report.issues:
        issues_rows.append(
            [
                issue.clause_name,
                issue.risk_level,
                issue.issue_summary,
                issue.suggested_redline,
                round(issue.confidence, 2),
            ]
        )

    decision_text = (
        f"Decision: {report.overall_decision}\n"
        f"Risk score: {report.overall_risk_score}\n"
        f"Type: {report.contract_type}\n\n"
        f"{report.executive_summary}"
    )

    return (
        decision_text,
        issues_rows,
        json.dumps(report_dict, indent=2),
        str(out_path),
    )


with gr.Blocks(title="Contract Review Copilot") as demo:
    gr.Markdown("# Contract Review Copilot")
    user_state = gr.State(value=None)
    with gr.Column(visible=True) as auth_view:
        gr.Markdown("## Login or Sign up")
        with gr.Tab("Login"):
            with gr.Row():
                username_input = gr.Textbox(label="Email")
                password_input = gr.Textbox(label="Password", type="password")
            login_btn = gr.Button("Login", variant="primary")
            login_status = gr.Textbox(label="Auth Status", interactive=False)

        with gr.Tab("Sign up"):
            with gr.Row():
                signup_username = gr.Textbox(label="New email")
                signup_password = gr.Textbox(label="New password", type="password")
            signup_role = gr.Dropdown(
                choices=["analyst", "legal_admin"],
                value="analyst",
                label="Role",
            )
            signup_btn = gr.Button("Create account")
            signup_status = gr.Textbox(label="Sign up status", interactive=False)

    with gr.Column(visible=False) as app_view:
        current_user = gr.Markdown("")
        gr.Markdown("Upload a contract and generate a legal review report.")
        gr.Markdown("Role policy: only `legal_admin` can override rubric text.")
        logout_btn = gr.Button("Logout")

        with gr.Row():
            file_input = gr.File(label="Contract file (.txt, .md, .pdf)")

        rubric_box = gr.Textbox(
            label="Scoring Rubric (editable)",
            value=load_default_rubric(),
            lines=12,
        )
        run_btn = gr.Button("Run AI Review", variant="primary")
        decision_box = gr.Textbox(label="Review Summary", lines=8)
        issues_table = gr.Dataframe(
            headers=["Clause", "Risk", "Issue", "Suggested redline", "Confidence"],
            datatype=["str", "str", "str", "str", "number"],
            label="Flagged Issues",
        )
        json_box = gr.Code(label="Full JSON Report", language="json")
        report_path = gr.Textbox(label="Saved report path")

    run_btn.click(
        fn=review_contract,
        inputs=[file_input, rubric_box, user_state],
        outputs=[decision_box, issues_table, json_box, report_path],
    )
    login_btn.click(
        fn=login,
        inputs=[username_input, password_input],
        outputs=[login_status, user_state, auth_view, app_view, current_user],
    )
    signup_btn.click(
        fn=signup,
        inputs=[signup_username, signup_password, signup_role],
        outputs=[signup_status],
    )
    logout_btn.click(
        fn=logout,
        inputs=[],
        outputs=[login_status, user_state, auth_view, app_view, current_user],
    )


if __name__ == "__main__":
    Path("outputs").mkdir(exist_ok=True)
    init_db()
    port_env = os.getenv("GRADIO_SERVER_PORT", "")
    demo.launch(
        server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
        server_port=int(port_env) if port_env else None,
        share=os.getenv("GRADIO_SHARE", "false").lower() == "true",
    )
