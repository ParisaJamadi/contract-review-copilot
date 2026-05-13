# Contract Risk Rubric (Demo)

Use this rubric to convert clause findings into a consistent overall score and decision.

## Severity weights

- low issue: +10 points
- medium issue: +20 points
- high issue: +35 points

Total score is capped at 100.

## Decision thresholds

- 0 to 20: approve
- 21 to 50: approve_with_edits
- 51 to 100: escalate

## Escalation override rules

Escalate immediately if any of the following appear:
- perpetual confidentiality for standard commercial info
- removed NDA exclusions (public/independent/rightfully received)
- unlimited liability for low-stakes contracts
- one-sided broad indemnity
- unrestricted customer rights to use data

## Evidence discipline

- Only flag issues grounded in contract text and/or playbook context.
- If evidence is missing, do not invent facts.
