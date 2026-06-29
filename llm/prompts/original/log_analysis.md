# Log Analysis Prompt

You are analyzing an OMEGA/MMSS auto-research JSONL log.

Context:
- Recent log lines: {{recent_logs}}
- Current config: {{config}}
- Current score: {{score}}
- Final metrics: {{metrics}}

Task:
- Identify the smallest useful next change.
- Prefer changes that are likely to improve the canonical score.
- Return strict JSON with keys: `asset`, `field`, `direction`, `magnitude`, `reason`.

