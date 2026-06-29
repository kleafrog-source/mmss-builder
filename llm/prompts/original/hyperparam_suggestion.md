# Hyperparameter Suggestion Prompt

You are assisting a local OMEGA/MMSS auto-research loop.

Context:
- Current config: {{config}}
- Current score: {{score}}
- Final metrics: {{metrics}}
- Recent log lines: {{recent_logs}}
- Ontology summary: {{ontology_summary}}

Task:
- Suggest exactly one small, testable change.
- Change only one field.
- Prefer a tiny numeric adjustment.
- Return strict JSON with keys: `asset`, `field`, `old_value`, `new_value`, `reason`.

Prefer changes that improve the canonical score and preserve determinism.

