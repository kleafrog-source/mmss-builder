from __future__ import annotations

import argparse
import copy
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib import error, request

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for auto_research/auto_loop.py") from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm.ollama_helper import run_ollama_with_fallback
from python.score import score_config, score_from_report


INSTRUCTIONS_PATH = PROJECT_ROOT / "auto_research" / "instructions.md"
OMEGA_CORE_PATH = PROJECT_ROOT / "omega_core.json"
ACTIVE_CONFIG_PATH = PROJECT_ROOT / "python" / "configs" / "active.yaml"
LOG_PATH = PROJECT_ROOT / "logs" / "auto_research_log.jsonl"
STOP_FLAG = PROJECT_ROOT / "auto_research" / "stop.flag"
PROMPTS_DIR = PROJECT_ROOT / "llm" / "prompts"
STATUS_PATH = PROJECT_ROOT / "auto_research" / "status.json"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(_read_text(path)) or {}


def _write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(_read_text(path)) if path.exists() and _read_text(path).strip() else {}


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_instructions() -> Dict[str, Any]:
    text = _read_text(INSTRUCTIONS_PATH)
    rules = {
        "target_score": 0.92,
        "epsilon": 0.0005,
        "stop_after_no_improve": 3,
        "max_rounds": 12,
    }
    for line in text.splitlines():
        lower = line.lower().strip()
        if lower.startswith("- target score:") or lower.startswith("target score:"):
            try:
                rules["target_score"] = float(lower.split(":", 1)[1].strip().rstrip("`"))
            except Exception:
                pass
        elif lower.startswith("- minimum improvement epsilon:") or lower.startswith("minimum improvement epsilon:"):
            try:
                rules["epsilon"] = float(lower.split(":", 1)[1].strip().rstrip("`"))
            except Exception:
                pass
        elif lower.startswith("- stop after") or lower.startswith("stop after"):
            digits = "".join(ch for ch in lower if ch.isdigit() or ch == ".")
            if digits:
                try:
                    rules["stop_after_no_improve"] = int(float(digits))
                except Exception:
                    pass
        elif lower.startswith("- default max rounds:") or lower.startswith("default max rounds:"):
            try:
                rules["max_rounds"] = int(float(lower.split(":", 1)[1].strip().rstrip("`")))
            except Exception:
                pass
    return rules


def _system_summary(omega_core: Dict[str, Any], max_chars: int = 1200) -> str:
    systems = omega_core.get("systems") or {}
    keys = list(systems)[:5]
    summary = []
    for key in keys:
        item = systems.get(key) or {}
        summary.append(f"{key}: {item.get('purpose', '')}")
    return "\n".join(summary)[:max_chars]


def _prompt_template(path: Path, context: Dict[str, Any]) -> str:
    text = _read_text(path)
    for key, value in context.items():
        text = text.replace(f"{{{{{key}}}}}", json.dumps(value, ensure_ascii=False, indent=2) if isinstance(value, (dict, list)) else str(value))
    return text


def _safe_round(value: float, digits: int = 6) -> float:
    return round(float(value), digits)


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _choose_asset(round_index: int) -> str:
    options = ["config", "mmss_spec", "prompt"]
    return options[round_index % len(options)]


def _numeric_keys(cfg: Dict[str, Any]) -> list[str]:
    return [key for key, value in cfg.items() if isinstance(value, (int, float))]


def _mutate_config(cfg: Dict[str, Any], rng: random.Random) -> Tuple[Dict[str, Any], str]:
    updated = copy.deepcopy(cfg)
    candidates = ["sigma", "delta_init", "warmup_epochs", "lr", "beta", "gamma", "delta_c", "eta_disp4"]
    field = rng.choice(candidates)
    old = updated.get(field)
    if field in {"warmup_epochs"}:
        delta = rng.choice([-1, 1])
        updated[field] = max(0, int(old or 0) + delta)
    elif field in {"sigma", "delta_init", "lr", "beta", "gamma", "delta_c", "eta_disp4"}:
        factor = rng.choice([0.95, 0.97, 1.03, 1.05])
        updated[field] = _safe_round((float(old or 0.0)) * factor)
    else:
        updated[field] = old
    return updated, f"config.{field}: {old} -> {updated.get(field)}"


def _mutate_mmss_spec(spec_path: Path, rng: random.Random) -> Tuple[Dict[str, Any], str]:
    data = _read_json(spec_path)
    updated = copy.deepcopy(data)
    if not updated:
        raise RuntimeError(f"Missing or empty MMSS spec: {spec_path}")

    if "unifiedmetrics" in updated and isinstance(updated["unifiedmetrics"], dict):
        metric_name = rng.choice(list(updated["unifiedmetrics"].keys()))
        metric = updated["unifiedmetrics"][metric_name]
        if isinstance(metric, dict) and isinstance(metric.get("current_value"), (int, float)):
            old = metric["current_value"]
            metric["current_value"] = _safe_round(float(old) * rng.choice([0.995, 1.005, 1.01]))
            desc = f"unifiedmetrics.{metric_name}.current_value: {old} -> {metric['current_value']}"
        else:
            old = metric
            updated["unifiedmetrics"][metric_name] = str(metric)
            desc = f"unifiedmetrics.{metric_name}: {old} -> {updated['unifiedmetrics'][metric_name]}"
    else:
        updated["purpose"] = f"{updated.get('purpose', '')} (loop-tuned)"
        desc = "purpose: appended loop-tuned marker"
    return updated, desc


def _mutate_prompt(prompt_path: Path, rng: random.Random) -> Tuple[str, str]:
    text = _read_text(prompt_path)
    old = text
    addition = "\n\nConstraint: keep the change minimal and preserve score determinism.\n"
    if "minimal" not in text.lower():
        text = text.rstrip() + addition
    else:
        text = text.replace("small, testable change", "small, testable change with a clear numeric direction", 1)
    return text, f"prompt_text: length {len(old)} -> {len(text)}"


def _try_ollama_suggestion(context: Dict[str, Any]) -> Dict[str, Any] | None:
    if os.environ.get("AUTO_RESEARCH_USE_OLLAMA", "").strip().lower() not in {"1", "true", "yes", "on"}:
        return None
    prompt_path = PROMPTS_DIR / "log_analysis.md"
    if not prompt_path.exists():
        return None
    try:
        with request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1.0):
            pass
    except Exception:
        return None
    prompt = _prompt_template(prompt_path, context)
    models = context.get("models") or [context.get("model", "qwen-coder-3b-cpu:latest")]
    try:
        response, model_used = run_ollama_with_fallback(prompt, models=models, timeout_seconds=10)
    except Exception:
        return None
    try:
        parsed = json.loads(response)
        if isinstance(parsed, dict):
            parsed["_model_used"] = model_used
        return parsed
    except Exception:
        return None


def _apply_candidate(
    asset_kind: str,
    cfg: Dict[str, Any],
    omega_core: Dict[str, Any],
    rng: random.Random,
    config_path: Path,
) -> Tuple[Path, str, Any]:
    if asset_kind == "config":
        updated, description = _mutate_config(cfg, rng)
        return config_path, description, updated
    if asset_kind == "mmss_spec":
        spec_path = _resolve_project_path(cfg.get("active_mmss_spec") or "mmss_specs/MMSSMETASYNTHESISULTIMATEv1.0.json")
        updated, description = _mutate_mmss_spec(spec_path, rng)
        return spec_path, description, updated
    prompt_path = _resolve_project_path(cfg.get("active_prompt") or "llm/prompts/hyperparam_suggestion.md")
    updated, description = _mutate_prompt(prompt_path, rng)
    return prompt_path, description, updated


def _persist_asset(path: Path, content: Any) -> None:
    if path.suffix.lower() in {".yaml", ".yml"}:
        if not isinstance(content, dict):
            raise TypeError("YAML assets must be dictionaries.")
        _write_yaml(path, content)
    elif path.suffix.lower() == ".json":
        if not isinstance(content, dict):
            raise TypeError("JSON assets must be dictionaries.")
        _write_json(path, content)
    else:
        if not isinstance(content, str):
            raise TypeError("Text assets must be strings.")
        path.write_text(content, encoding="utf-8")


def _write_status(payload: Dict[str, Any]) -> None:
    STATUS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _print_progress(message: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{stamp}] {message}", flush=True)


def _load_report_score(report: Dict[str, Any]) -> float:
    return score_from_report(report)


def _log_round(entry: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_loop(max_rounds: int | None = None, dry_run: bool = False, config_path: Path = ACTIVE_CONFIG_PATH) -> Dict[str, Any]:
    instructions = _load_instructions()
    omega_core = _read_json(OMEGA_CORE_PATH)
    if not omega_core:
        raise RuntimeError("omega_core.json is missing or empty; create the ontology before running the loop.")

    cfg = _read_yaml(config_path)
    if not cfg:
        raise RuntimeError(f"Missing active config: {config_path}")

    target_score = float(cfg.get("target_score", instructions["target_score"]))
    epsilon = float(cfg.get("epsilon", instructions["epsilon"]))
    plateau_limit = int(cfg.get("stop_after_no_improve", instructions["stop_after_no_improve"]))
    max_rounds = int(max_rounds or cfg.get("max_rounds", instructions["max_rounds"]))
    prompt_path = _resolve_project_path(cfg.get("active_prompt") or "llm/prompts/work/hyperparam_suggestion.md")
    if "llm\\prompts\\work" not in str(prompt_path).replace("/", "\\"):
        raise RuntimeError(f"Refusing to mutate non-work prompt path: {prompt_path}")

    rng = random.Random(42)
    baseline_score, baseline_report, baseline_report_path = score_config(config_path)
    best_score = baseline_score
    no_improve = 0
    round_summaries: list[Dict[str, Any]] = []
    _write_status({
        "running": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "best_score": best_score,
        "baseline_score": baseline_score,
        "round": -1,
        "message": "initialized",
    })
    _print_progress(f"Initialized. baseline_score={baseline_score}")

    for round_index in range(max_rounds):
        if STOP_FLAG.exists():
            _print_progress("Stop flag detected. Exiting.")
            break
        asset_kind = _choose_asset(round_index)
        current_cfg = _read_yaml(config_path)
        candidate_path, change_description, candidate_content = _apply_candidate(
            asset_kind, current_cfg, omega_core, rng, config_path
        )
        before_bytes = candidate_path.read_text(encoding="utf-8") if candidate_path.exists() else ""

        suggestion = _try_ollama_suggestion(
            {
                "config": current_cfg,
                "score": best_score,
                "metrics": baseline_report.get("final_metrics", {}),
                "recent_logs": _read_text(LOG_PATH)[-2000:],
                "ontology_summary": _system_summary(omega_core),
                "model": current_cfg.get("ollama_model", "qwen-coder-3b-cpu:latest"),
                "models": current_cfg.get("ollama_models") or ["qwen-coder-3b-cpu:latest", "qwen2.5-coder:3b", "llama3"],
            }
        )

        if not dry_run:
            _persist_asset(candidate_path, candidate_content)

        new_score, new_report, new_report_path = score_config(config_path)
        decision = "kept" if new_score > best_score + epsilon else "reverted"
        metrics = new_report.get("final_metrics", {})
        summary_text = (
            f"asset={asset_kind} change={change_description} decision={decision} "
            f"score={new_score:.6f} V={metrics.get('V')} S={metrics.get('S')} "
            f"clean={metrics.get('test_acc_clean')} energy={metrics.get('energy_rel_v4')}"
        )

        if decision == "reverted" and not dry_run:
            candidate_path.write_text(before_bytes, encoding="utf-8")
        else:
            best_score = new_score
            baseline_report = new_report
            baseline_report_path = new_report_path

        round_entry = {
            "round": round_index,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "asset": str(candidate_path),
            "asset_kind": asset_kind,
            "change_description": change_description,
            "baseline_score_before": baseline_score,
            "new_score": new_score,
            "decision": decision,
            "score_delta": round(new_score - baseline_score, 6),
            "submetrics": new_report.get("final_metrics", {}),
            "report_path": str(new_report_path),
            "baseline_report_path": str(baseline_report_path),
            "ollama_suggestion": suggestion,
            "summary_text": summary_text,
        }
        _log_round(round_entry)
        round_summaries.append(round_entry)
        _write_status({
            "running": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config_path": str(config_path),
            "round": round_index,
            "asset": str(candidate_path),
            "decision": decision,
            "best_score": best_score,
            "current_score": new_score,
            "summary_text": summary_text,
            "report_path": str(new_report_path),
        })
        _print_progress(summary_text)

        if decision == "kept":
            baseline_score = new_score
            no_improve = 0
        else:
            no_improve += 1

        if best_score >= target_score or no_improve >= plateau_limit:
            _print_progress("Stop condition reached.")
            break

    _write_status({
        "running": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "baseline_score": baseline_score,
        "best_score": best_score,
        "rounds_completed": len(round_summaries),
        "message": "completed",
    })
    return {
        "baseline_score": baseline_score,
        "best_score": best_score,
        "rounds": round_summaries,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local OMEGA/MMSS auto-research loop.")
    parser.add_argument("--max-rounds", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", default=str(ACTIVE_CONFIG_PATH))
    args = parser.parse_args(argv)

    result = run_loop(max_rounds=args.max_rounds, dry_run=args.dry_run, config_path=Path(args.config))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
