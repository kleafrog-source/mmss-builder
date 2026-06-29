# Goal

Run a fully local, deterministic auto-research loop around OMEGA/MMSS assets
and local Ollama integration.

# Rules

- Only mutate ASSET files:
  - `python/configs/*.yaml`
  - `mmss_specs/*.json`
  - `llm/prompts/*.md`
- Do not modify the scoring definition in `python/score.py`.
- Do not modify `omega_core.json` after it is created.
- Change only one asset per round.
- Keep each change small and reversible.

# Metric

Maximize the numeric score returned by `python/score.py`.

# Targets

- Target score: `>= 0.92`
- Minimum improvement epsilon: `0.0005`
- Stop after `3` consecutive non-improving rounds
- Default max rounds: `12`

# Stop Conditions

- `auto_research/stop.flag` exists
- Target score reached
- Plateau condition reached
- Manual stop from the operator

