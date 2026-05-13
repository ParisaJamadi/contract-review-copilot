import json
from pathlib import Path

from src.contract_copilot.config import DATA_DIR
from src.contract_copilot.pipeline import run_review


def evaluate():
    contracts_dir = DATA_DIR / "contracts"
    labels_path = DATA_DIR / "gold_labels.json"
    labels = json.loads(labels_path.read_text(encoding="utf-8"))

    total = len(labels)
    decision_hits = 0
    issue_count_hits = 0
    details = []

    for item in labels:
        file_path = contracts_dir / item["file"]
        contract_text = file_path.read_text(encoding="utf-8")
        report = run_review(contract_text)

        decision_ok = report.overall_decision == item["expected_decision"]
        issues_ok = len(report.issues) >= item["expected_min_issues"]
        decision_hits += int(decision_ok)
        issue_count_hits += int(issues_ok)

        details.append(
            {
                "file": item["file"],
                "expected_decision": item["expected_decision"],
                "actual_decision": report.overall_decision,
                "expected_min_issues": item["expected_min_issues"],
                "actual_issues": len(report.issues),
                "decision_match": decision_ok,
                "issues_match": issues_ok,
            }
        )

    results = {
        "total_contracts": total,
        "decision_accuracy": decision_hits / total if total else 0,
        "min_issue_threshold_accuracy": issue_count_hits / total if total else 0,
        "details": details,
    }

    out_path = Path("outputs") / "eval_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"\nSaved evaluation results to: {out_path}")


if __name__ == "__main__":
    evaluate()
