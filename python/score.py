from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from python.validate_metrics import DEFAULT_CONFIG, run_validation


def score_from_report(report: Dict[str, Any]) -> float:
    metrics = report.get("final_metrics") or {}
    clean = float(metrics.get("test_acc_clean", 0.0))
    energy = float(metrics.get("energy_rel_v4", 0.0))
    v = float(metrics.get("V", 0.0))
    s = float(metrics.get("S", 0.0))
    goldenscore = float(metrics.get("goldenscore", 0.0))
    latency = float(metrics.get("inference_latency_ms", 0.0))
    eta = float(metrics.get("eta_tern", 0.0))
    zeta = float(metrics.get("zeta_Z3", 0.0))

    score = (
        clean
        - 0.10 * energy
        + 0.01 * v
        - 0.05 * s
        + 0.02 * goldenscore
        - 0.0005 * latency
        + 0.01 * eta
        + 0.01 * zeta
    )
    return round(score, 6)


def score_config(config_path: Path | str = DEFAULT_CONFIG) -> tuple[float, Dict[str, Any], Path]:
    report, report_path = run_validation(config_path)
    return score_from_report(report), report, report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the canonical OMEGA/MMSS score.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    score, report, report_path = score_config(Path(args.config))
    if args.json:
        print(json.dumps({"score": score, "report_path": str(report_path), "report": report}, indent=2, ensure_ascii=False))
    else:
        print(score)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

