# Project Documentation

## Problem framing

The legal team receives many similar low-stakes contracts (NDAs, simple order forms). Most are mostly boilerplate, but every contract still needs manual review. During high sales periods, this creates a queue and slows deal flow.

The practical question is not “Can AI replace legal review?” but:

**How can AI safely handle repeatable parts of review so legal can focus on true exceptions?**

---

## Approach used

### 1. AI-assisted triage, not blind automation

The system reviews incoming contracts and produces:

- contract type classification
- overall decision (`approve`, `approve_with_edits`, `escalate`)
- risk score
- clause-level issues
- suggested fallback language

High-risk cases are still escalated to human legal review.

### 2. Retrieval-Augmented Generation (RAG)

To avoid generic answers, the assistant retrieves relevant policy text from an internal playbook before generating its analysis.

- Knowledge source: `data/playbook.md`
- Vector store: ChromaDB
- Retrieval used as context for each review

This improves consistency and keeps outputs aligned with internal policy language.

### 3. Rubric-based deterministic decisioning

A key design choice is separating:

- **issue extraction** (LLM task)
- **final score/decision** (rule-based task)

The model identifies issues, but the final decision is enforced by a rubric (`data/rubric.md`) in code. This reduces drift and improves auditability.

### 4. User flow and governance

- Auth-first interface (login/sign-up shown before app)
- Role-aware behavior (`legal_admin`, `analyst`)
- JSON audit log for each run: user, role, contract, decision, score, full report

---

## Methods and tools

- Language: Python
- LLM orchestration: LangChain
- Retrieval store: ChromaDB
- UI: Gradio
- Structured outputs: Pydantic
- Data formats: JSON / JSONL for local auth and logs

---

## Responsible AI considerations

This prototype includes practical safety controls:

- Grounding via internal policy retrieval
- Prompt instruction to avoid inventing facts
- Deterministic rubric for final decision
- Human-in-the-loop escalation for higher risk
- Audit logging for traceability

This is a legal-assist tool, not legal advice automation.

---

## Why this design

The design prioritizes:

- fast prototyping
- clear explainability
- policy control
- low operational setup

It is intentionally simple enough to run locally, but structured so components can be swapped for production systems later.

---

## Future improvements

### Frontend and product experience

- Replace Gradio with React frontend + FastAPI backend
- Add dashboard for queue view, escalation trends, reviewer actions

### Storage and enterprise controls

- Move auth/audit from JSON to PostgreSQL
- Add SSO, RBAC, and proper secret management

### Performance and scale

- Batch and parallel contract processing
- Worker queue for month-end/quarter-end volume spikes

### Model quality and evaluation

- Build a larger labeled evaluation set
- Track precision/recall by clause type
- Add hallucination and citation quality checks
- Add human feedback loop to improve prompts/rubric

### Document understanding

- Add multimodal support for scanned PDFs and images (OCR + vision model)
- Better table extraction for order forms and pricing annexes

### Cloud deployment

- Deploy on AWS (e.g., ECS/Fargate + managed DB + object storage)
- Add monitoring, alerting, and usage analytics

---

## Conclusion

This prototype demonstrates a realistic way AI can reduce legal review load without removing human oversight. It is designed to be useful now and extensible toward a production-grade legal ops assistant.

