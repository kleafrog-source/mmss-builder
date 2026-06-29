# MMSS Synthesis Prompt

You are refining a local MMSS JSON asset inside an auto-research loop.

Context:
- Selected MMSS system: {{system_id}}
- Current spec: {{spec}}
- Current score: {{score}}
- Final metrics: {{metrics}}
- Ontology summary: {{ontology_summary}}

Task:
- Propose one small JSON change that improves clarity or score influence.
- Keep the change syntactically safe.
- Only touch one JSON path.
- Return strict JSON with keys: `json_path`, `old_value`, `new_value`, `reason`.

