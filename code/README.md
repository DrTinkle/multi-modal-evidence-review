# Multi-Modal Evidence Review Solution

## Run

Start the local VLM server first. The default assumes an OpenAI-compatible
endpoint at `http://127.0.0.1:1234` with model `qwen/qwen3-vl-4b`.

From the repository root:

```bash
python code/main.py --input dataset/claims.csv --output output.csv --dataset-root dataset
```

This writes `output.csv` with the required schema.

Useful options:

```bash
python code/main.py \
  --base-url http://127.0.0.1:1234 \
  --model qwen/qwen3-vl-4b \
  --cache code/cache/vlm_cache.json \
  --log code/logs/model_io.jsonl
```

## Evaluate

```bash
python code/evaluation/main.py
```

This writes:

- `code/evaluation/sample_predictions.csv`
- `code/evaluation/evaluation_report.md`

## Approach

The solution uses a local VLM evidence layer. It sends each claim and its submitted images to the local OpenAI-compatible Qwen endpoint, asks for strict JSON, normalizes model output to the allowed schema, merges user-history risk flags, ignores instruction-like text as evidence, and validates every row before writing the CSV.

Generated model responses are cached by claim/image hash. Per-claim model input/output logs are written as JSONL so the decision path is auditable without storing large base64 image payloads in the log.
