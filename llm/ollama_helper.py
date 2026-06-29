from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib import error, request


try:
    from mmss_core.ai.ollama import LocalOllamaAPI, OllamaAPIError
except Exception:  # pragma: no cover - fallback for isolated environments
    LocalOllamaAPI = None  # type: ignore[assignment]

    class OllamaAPIError(RuntimeError):
        pass


def _run_ollama_cli(prompt: str, model: str) -> str:
    ollama = shutil.which("ollama")
    if not ollama:
        raise OllamaAPIError("ollama CLI is not available.")

    proc = subprocess.run(
        [ollama, "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise OllamaAPIError(proc.stderr.strip() or "ollama CLI failed.")
    return proc.stdout.strip()


def _run_ollama_http(prompt: str, model: str, base_url: str, timeout_seconds: int) -> str:
    if LocalOllamaAPI is None:
        raise OllamaAPIError("LocalOllamaAPI is unavailable.")
    api = LocalOllamaAPI(model=model, base_url=base_url, timeout_seconds=timeout_seconds)
    return api.get_response(prompt)


def _request_json(url: str, timeout_seconds: int) -> dict[str, Any]:
    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise OllamaAPIError(f"Ollama HTTP {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise OllamaAPIError(f"Ollama is unavailable at {url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise OllamaAPIError("Invalid JSON response from Ollama.") from exc


def list_ollama_models(base_url: str = "http://127.0.0.1:11434", timeout_seconds: int = 2) -> list[dict[str, Any]]:
    payload = _request_json(f"{base_url.rstrip('/')}/api/tags", timeout_seconds)
    models = payload.get("models") or []
    if not isinstance(models, list):
        return []
    return [model for model in models if isinstance(model, dict)]


def run_ollama(
    prompt: str,
    model: str = "qwen-coder-3b-cpu:latest",
    base_url: str = "http://127.0.0.1:11434",
    timeout_seconds: int = 120,
) -> str:
    """Run a prompt against local Ollama, using HTTP first and CLI as fallback."""

    if LocalOllamaAPI is not None:
        try:
            return _run_ollama_http(prompt, model=model, base_url=base_url, timeout_seconds=timeout_seconds)
        except Exception:
            pass

    try:
        return _run_ollama_cli(prompt, model=model)
    except Exception as exc:
        raise OllamaAPIError(f"Local Ollama unavailable: {exc}") from exc


def run_ollama_with_fallback(
    prompt: str,
    models: Iterable[str],
    base_url: str = "http://127.0.0.1:11434",
    timeout_seconds: int = 120,
) -> tuple[str, str]:
    last_error: Exception | None = None
    for model in models:
        try:
            return run_ollama(prompt, model=model, base_url=base_url, timeout_seconds=timeout_seconds), model
        except Exception as exc:
            last_error = exc
    if last_error is None:
        raise OllamaAPIError("No Ollama models were provided.")
    raise OllamaAPIError(f"All Ollama models failed: {last_error}") from last_error


def ollama_available(base_url: str = "http://127.0.0.1:11434", model: str = "qwen-coder-3b-cpu:latest") -> bool:
    try:
        run_ollama("Reply with exactly: ok", model=model, base_url=base_url, timeout_seconds=10)
        return True
    except Exception:
        return False
