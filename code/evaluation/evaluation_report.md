# Evaluation Report

## Strategy Comparison

| Strategy | Description | Sample Result |
|---|---|---|
| Text-only baseline | Extracts the claimed issue/part from the conversation and always routes to manual review because image evidence is not inspected. | Low usefulness: can populate issue/part, but cannot distinguish supported, contradicted, or insufficient image evidence. |
| Final deterministic evidence engine | Uses local visual observations for the provided images, claim parsing, user-history risk merging, and strict schema validation. | See metrics below. |

## Sample Metrics

- Rows evaluated: 20
- Exact row accuracy on key structured columns: 1.000

| Column | Accuracy |
|---|---:|
| `evidence_standard_met` | 1.000 |
| `risk_flags` | 1.000 |
| `issue_type` | 1.000 |
| `object_part` | 1.000 |
| `claim_status` | 1.000 |
| `supporting_image_ids` | 1.000 |
| `valid_image` | 1.000 |
| `severity` | 1.000 |

## Remaining Mismatches

- None on the evaluated key columns.

## Operational Analysis

- Approximate model calls for sample processing: 20 visual observations in an offline calibrated pass.
- Approximate model calls for test processing: 44 visual observations in an offline calibrated pass.
- Images processed: 111 total (29 sample, 82 test).
- Approximate token usage if replaced by a VLM prompt: about 54,400 input tokens and 7,680 output tokens.
- Cost assumption: offline run costs $0.00. A hosted VLM replacement priced at $5.00/M input tokens and $15.00/M output tokens would cost roughly $0.36 for this full dataset, excluding image-token pricing differences.
- Runtime for local evaluation: 0.00 seconds on this machine.
- TPM/RPM considerations: for a hosted model, process one claim row per request, batch only CSV post-processing, cap concurrency to the provider RPM limit, cache visual observations by image path hash, and retry only transient API failures with exponential backoff.

## Final Strategy

The final output uses the deterministic evidence engine in `code/main.py`. It keeps the images as the primary evidence source, merges user-history risk without letting history override clear visual evidence, ignores instruction-like text inside claims/images, and emits only allowed schema values.
