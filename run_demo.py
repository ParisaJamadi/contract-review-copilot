from pathlib import Path

from src.contract_copilot.pipeline import run_review, save_report


def main() -> None:
    sample = Path("data/contracts/nda_sample_2.txt")
    text = sample.read_text(encoding="utf-8")
    report = run_review(text)
    out_path = save_report(report)
    print("Decision:", report.overall_decision)
    print("Risk score:", report.overall_risk_score)
    print("Report:", out_path)


if __name__ == "__main__":
    main()
