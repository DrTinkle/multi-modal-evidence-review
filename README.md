# Multi-Modal Evidence Review

A local multimodal evidence-review system for validating damage claims involving cars, laptops, and packages.

## Overview

The solution analyzes claim conversations, submitted images, user history, and evidence requirements to determine whether image evidence:

- supports the claim
- contradicts the claim
- provides insufficient information

Images are treated as the primary source of truth. User history contributes risk context but does not override clear visual evidence.

## Approach

The system uses a local Vision Language Model (Qwen3-VL-4B) to:

- identify visible damage
- determine affected object parts
- evaluate evidence sufficiency
- classify claim status
- generate concise evidence-based justifications

Deterministic validation layers normalize model output, enforce schema compliance, merge risk signals, and fail closed to `not_enough_information` when model responses are invalid or incomplete.

## Features

- Local VLM inference via OpenAI-compatible endpoint
- Image preprocessing and resizing
- Response caching using image and claim hashes
- Per-claim JSONL audit logs
- CSV schema validation
- Evaluation workflow for sample claims

## Run

```bash
python code/main.py --input dataset/claims.csv --output output.csv --dataset-root dataset
```

## Evaluate

```bash
python code/evaluation/main.py
```

The evaluation workflow generates predictions for the sample dataset and produces an evaluation report comparing model outputs against expected results.
