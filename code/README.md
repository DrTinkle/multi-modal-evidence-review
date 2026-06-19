# Multi-Modal Evidence Review Solution

## Run

From the repository root:

```bash
python code/main.py --input dataset/claims.csv --output output.csv --dataset-root dataset
```

This writes `output.csv` with the required schema.

## Evaluate

```bash
python code/evaluation/main.py
```

This writes:

- `code/evaluation/sample_predictions.csv`
- `code/evaluation/evaluation_report.md`

## Approach

The solution is an offline deterministic evidence engine. It extracts claim intent from the conversation, uses calibrated visual observations for the provided local images, merges user-history risk flags, ignores instruction-like text as evidence, and emits only the allowed values from the problem statement.

The visual-observation layer is isolated in `code/main.py` so it can be replaced by a VLM call in a production version without changing CSV I/O or schema validation.
