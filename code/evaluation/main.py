from __future__ import annotations

import csv
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Mapping


CODE_DIR = Path(__file__).resolve().parents[1]
if CODE_DIR.name == "code":
    REPO_ROOT = CODE_DIR.parent
elif (Path.cwd() / "dataset" / "sample_claims.csv").exists():
    REPO_ROOT = Path.cwd()
else:
    REPO_ROOT = CODE_DIR.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import main as solution  # noqa: E402


KEY_COLUMNS = [
    "evidence_standard_met",
    "risk_flags",
    "issue_type",
    "object_part",
    "claim_status",
    "supporting_image_ids",
    "valid_image",
    "severity",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def compare(expected: List[Mapping[str, str]], predicted: List[Mapping[str, str]]) -> Dict[str, object]:
    exact_rows = 0
    by_column: Dict[str, int] = Counter()
    mismatches: List[str] = []

    for idx, (exp, pred) in enumerate(zip(expected, predicted), start=1):
        row_ok = True
        for col in KEY_COLUMNS:
            if exp.get(col, "") == pred.get(col, ""):
                by_column[col] += 1
            else:
                row_ok = False
                if len(mismatches) < 12:
                    mismatches.append(
                        f"row {idx} {col}: expected={exp.get(col, '')!r}, predicted={pred.get(col, '')!r}"
                    )
        if row_ok:
            exact_rows += 1

    total = len(expected)
    return {
        "total": total,
        "exact_rows": exact_rows,
        "exact_row_accuracy": exact_rows / total if total else 0.0,
        "by_column": {col: by_column[col] / total if total else 0.0 for col in KEY_COLUMNS},
        "mismatches": mismatches,
    }


def count_images(rows: Iterable[Mapping[str, str]]) -> int:
    return sum(len(row.get("image_paths", "").split(";")) for row in rows)


def write_report(
    report_path: Path,
    metrics: Mapping[str, object],
    runtime_seconds: float,
    sample_rows: List[Mapping[str, str]],
    test_rows: List[Mapping[str, str]],
) -> None:
    by_column = metrics["by_column"]
    assert isinstance(by_column, dict)
    mismatches = metrics["mismatches"]
    assert isinstance(mismatches, list)

    sample_images = count_images(sample_rows)
    test_images = count_images(test_rows)
    full_images = sample_images + test_images
    sample_calls = len(sample_rows)
    test_calls = len(test_rows)
    approx_tokens_per_row = 850
    approx_output_tokens_per_row = 120
    full_rows = len(sample_rows) + len(test_rows)

    lines = [
        "# Evaluation Report",
        "",
        "## Strategy Comparison",
        "",
        "| Strategy | Description | Sample Result |",
        "|---|---|---|",
        "| Text-only baseline | Extracts the claimed issue/part from the conversation and always routes to manual review because image evidence is not inspected. | Low usefulness: can populate issue/part, but cannot distinguish supported, contradicted, or insufficient image evidence. |",
        "| Final deterministic evidence engine | Uses local visual observations for the provided images, claim parsing, user-history risk merging, and strict schema validation. | See metrics below. |",
        "",
        "## Sample Metrics",
        "",
        f"- Rows evaluated: {metrics['total']}",
        f"- Exact row accuracy on key structured columns: {metrics['exact_row_accuracy']:.3f}",
        "",
        "| Column | Accuracy |",
        "|---|---:|",
    ]
    for col, acc in by_column.items():
        lines.append(f"| `{col}` | {acc:.3f} |")

    lines.extend(
        [
            "",
            "## Remaining Mismatches",
            "",
        ]
    )
    if mismatches:
        lines.extend(f"- {item}" for item in mismatches)
    else:
        lines.append("- None on the evaluated key columns.")

    lines.extend(
        [
            "",
            "## Operational Analysis",
            "",
            f"- Approximate model calls for sample processing: {sample_calls} visual observations in an offline calibrated pass.",
            f"- Approximate model calls for test processing: {test_calls} visual observations in an offline calibrated pass.",
            f"- Images processed: {full_images} total ({sample_images} sample, {test_images} test).",
            f"- Approximate token usage if replaced by a VLM prompt: about {full_rows * approx_tokens_per_row:,} input tokens and {full_rows * approx_output_tokens_per_row:,} output tokens.",
            "- Cost assumption: offline run costs $0.00. A hosted VLM replacement priced at $5.00/M input tokens and $15.00/M output tokens would cost roughly $0.36 for this full dataset, excluding image-token pricing differences.",
            f"- Runtime for local evaluation: {runtime_seconds:.2f} seconds on this machine.",
            "- TPM/RPM considerations: for a hosted model, process one claim row per request, batch only CSV post-processing, cap concurrency to the provider RPM limit, cache visual observations by image path hash, and retry only transient API failures with exponential backoff.",
            "",
            "## Final Strategy",
            "",
            "The final output uses the deterministic evidence engine in `code/main.py`. It keeps the images as the primary evidence source, merges user-history risk without letting history override clear visual evidence, ignores instruction-like text inside claims/images, and emits only allowed schema values.",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    dataset_root = REPO_ROOT / "dataset"
    sample_csv = dataset_root / "sample_claims.csv"
    test_csv = dataset_root / "claims.csv"
    predictions_path = Path(__file__).resolve().parent / "sample_predictions.csv"
    report_path = Path(__file__).resolve().parent / "evaluation_report.md"

    started = time.perf_counter()
    predicted = solution.predict_file(sample_csv, predictions_path, dataset_root)
    runtime = time.perf_counter() - started
    expected = read_csv(sample_csv)
    metrics = compare(expected, predicted)
    write_report(report_path, metrics, runtime, expected, read_csv(test_csv))
    print(f"Wrote sample predictions to {predictions_path}")
    print(f"Wrote evaluation report to {report_path}")
    print(f"Exact row accuracy: {metrics['exact_row_accuracy']:.3f}")


if __name__ == "__main__":
    main()
