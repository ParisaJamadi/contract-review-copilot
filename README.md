# Contract Review Copilot

This prototype shows how AI can support a small legal team reviewing common low-stakes contracts (mainly mutual NDAs and simple order forms).

The goal is to reduce queue pressure by handling repeatable review work first, while still escalating risky cases to legal.

## What the app does

- Reviews uploaded contracts and classifies them as `approve`, `approve_with_edits`, or `escalate`
- Flags risky clauses and suggests practical fallback language
- Uses retrieval from an internal legal playbook (RAG with ChromaDB)
- Applies a rubric-based scoring policy for consistent decisions
- Requires login before use, with role-based behavior
- Writes review audit logs to JSON for traceability

## Short demo flow

1. Login to the app.
2. Upload a contract file (`.txt`, `.md`, or `.pdf`).
3. Review (or update) the rubric policy shown in the UI.
4. Click **Run AI Review**.
5. Review:
   - overall decision
   - risk score
   - flagged clauses
   - suggested redlines
   - full JSON output
6. Note that final score and decision are rubric-enforced for consistency.

## Tech stack

- Python
- LangChain
- ChromaDB
- Gradio

## Local setup (Windows / PowerShell)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` in the project root:

```env
OPENAI_API_KEY=your_key_here
APP_ADMIN_EMAIL=admin@example.com
APP_ADMIN_PASSWORD=change_me_admin_password
APP_ANALYST_EMAIL=analyst@example.com
APP_ANALYST_PASSWORD=change_me_analyst_password
```

Build the vector index:

```bash
python -m src.contract_copilot.ingest
```

Run the app:

```bash
python ui/app.py
```

If `7860` is busy:

```bash
$env:GRADIO_SERVER_PORT="7861"
python ui/app.py
```

## Default login

- Admin: `admin@example.com` / `change_me_admin_password`
- Analyst: `analyst@example.com` / `change_me_analyst_password`

## Project layout

- `ui/app.py`: Gradio UI
- `src/contract_copilot/pipeline.py`: review pipeline and rubric enforcement
- `src/contract_copilot/retrieval.py`: RAG retrieval logic
- `src/contract_copilot/ingest.py`: playbook indexing
- `src/contract_copilot/db.py`: JSON auth and audit logging
- `data/playbook.md`: legal playbook knowledge source
- `data/rubric.md`: scoring and escalation policy
- `outputs/review_logs.jsonl`: review audit trail

## Why these AI choices (plain language)

- Why RAG (Retrieval-Augmented Generation): the system first retrieves relevant internal policy text from the legal playbook, then uses that context during review. This keeps outputs aligned with company rules instead of generic AI answers.
- What hallucination means: a hallucination is when AI states something that is not supported by the contract or policy text. In legal review, that can create risk.
- How hallucination is reduced here: the prompt explicitly tells the model not to invent facts, retrieved playbook context is provided on each run, and final score/decision are enforced by rubric rules.
- What prompt engineering means: prompt engineering is writing clear instructions for model behavior and output format. Here it improves consistency, traceability, and review quality.
- Why structured JSON output: the review is returned in a fixed schema so results are predictable, easier to validate, and easier to integrate into legal workflows.
- Why role-based access: policy controls are separated from day-to-day usage, so legal admins can manage rubric policy while analysts run reviews.
- Why audit logs matter: each run is recorded with user, file, decision, and score, which supports accountability and later quality analysis.

## Notes

- Sample contracts and policies are synthetic for demo use.
- This is not legal advice.
