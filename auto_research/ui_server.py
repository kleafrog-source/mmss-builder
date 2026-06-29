from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, render_template_string, abort

from llm.ollama_helper import list_ollama_models


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = PROJECT_ROOT / "logs" / "auto_research_log.jsonl"
STATUS_PATH = PROJECT_ROOT / "auto_research" / "status.json"
STOP_FLAG = PROJECT_ROOT / "auto_research" / "stop.flag"
DEFAULT_CONFIG = PROJECT_ROOT / "python" / "configs" / "active.yaml"
LOOP_PYTHON = PROJECT_ROOT / "mmss_core" / "ai" / "orchestrator-mmss" / "venv" / "Scripts" / "python.exe"

app = Flask(__name__)

_process_lock = threading.Lock()
_current_process: subprocess.Popen[str] | None = None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _tail_jsonl(path: Path, limit: int = 25) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    items: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return items


def _allowed_file(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    resolved = path.resolve()
    if PROJECT_ROOT not in resolved.parents and resolved != PROJECT_ROOT:
        abort(400, description="Path outside project root")
    return resolved


def _file_preview_candidates() -> list[str]:
    candidates = [
        "auto_research/TASK.md",
        "auto_research/TASK.original.md",
        "auto_research/instructions.md",
        "auto_research/status.json",
        "python/configs/active.yaml",
        "python/configs/omega_base.yaml",
        "python/configs/omega_experiment_01.yaml",
        "python/configs/omega_loop_test.yaml",
        "llm/prompts/work/hyperparam_suggestion.md",
        "llm/prompts/work/mmss_synthesis.md",
        "llm/prompts/work/log_analysis.md",
    ]
    return candidates


def _start_loop_process(
    config_path: str,
    max_rounds: int,
    use_ollama: bool,
    ollama_model: str | None = None,
    ollama_models: str | None = None,
) -> dict[str, Any]:
    global _current_process
    with _process_lock:
        if _current_process and _current_process.poll() is None:
            return {"ok": False, "error": "loop already running"}
        if STOP_FLAG.exists():
            STOP_FLAG.unlink()
        env = os.environ.copy()
        if use_ollama:
            env["AUTO_RESEARCH_USE_OLLAMA"] = "1"
        else:
            env.pop("AUTO_RESEARCH_USE_OLLAMA", None)
        if ollama_model:
            env["AUTO_RESEARCH_OLLAMA_MODEL"] = ollama_model
        if ollama_models:
            env["AUTO_RESEARCH_OLLAMA_MODELS"] = ollama_models
        env["PYTHONUNBUFFERED"] = "1"
        python_executable = str(LOOP_PYTHON) if LOOP_PYTHON.exists() else sys.executable
        cmd = [
            python_executable,
            "-u",
            "-m",
            "auto_research.auto_loop",
            "--config",
            config_path,
            "--max-rounds",
            str(max_rounds),
        ]
        _current_process = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            text=True,
        )
        return {"ok": True, "pid": _current_process.pid}


def _stop_loop_process() -> dict[str, Any]:
    global _current_process
    STOP_FLAG.write_text("stop\n", encoding="utf-8")
    with _process_lock:
        proc = _current_process
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        _current_process = None
    return {"ok": True}


INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Auto Research Control</title>
  <style>
    :root { color-scheme: dark; --bg: #0b1020; --panel: #10192f; --panel2:#0e1630; --text:#e8eefc; --muted:#93a4c3; --accent:#6ee7ff; --accent2:#8b5cf6; --line:#24304e; }
    body { margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background: radial-gradient(circle at top, #172449 0, #0b1020 40%, #070b16 100%); color:var(--text); }
    header { padding: 24px 28px 12px; border-bottom:1px solid var(--line); }
    h1 { margin:0; font-size: 22px; letter-spacing:.02em; }
    main { display:grid; grid-template-columns: 1.1fr .9fr; gap:16px; padding:16px 28px 24px; }
    .card { background: linear-gradient(180deg, rgba(16,25,47,.95), rgba(10,14,29,.95)); border:1px solid var(--line); border-radius:16px; padding:16px; box-shadow: 0 24px 60px rgba(0,0,0,.25); }
    .grid { display:grid; gap:12px; }
    .row { display:flex; gap:12px; flex-wrap:wrap; }
    label { font-size:12px; color:var(--muted); display:block; margin-bottom:6px; }
    input, select, button, textarea { background:#07101f; color:var(--text); border:1px solid #2a3857; border-radius:10px; padding:10px 12px; font:inherit; }
    input, select, textarea { width:100%; box-sizing:border-box; }
    select[multiple] { min-height: 164px; }
    button { cursor:pointer; background: linear-gradient(135deg, #0f172a, #172554); }
    button.primary { border-color: #2dd4bf; }
    button.danger { border-color: #ef4444; }
    button:hover { filter: brightness(1.08); }
    pre { white-space: pre-wrap; word-break: break-word; background:#07101f; border:1px solid #24304e; border-radius:12px; padding:12px; min-height: 120px; overflow:auto; }
    table { width:100%; border-collapse: collapse; font-size: 13px; }
    th, td { text-align:left; padding:8px; border-bottom:1px solid #1f2a43; vertical-align: top; }
    .muted { color:var(--muted); }
    .pill { display:inline-block; padding:4px 10px; border-radius:999px; background:#0f1a33; border:1px solid #24304e; margin-right:6px; }
    .split { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .file-box { min-height: 420px; }
    @media (max-width: 1100px) { main { grid-template-columns: 1fr; } .split { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>Local Auto Research Control</h1>
    <div class="muted">Start, stop, inspect logs, and compare immutable vs work files.</div>
  </header>
  <main>
    <section class="card grid">
      <div class="row">
        <div style="flex:1 1 220px;">
          <label>Config</label>
          <select id="config_path">
            <option value="python/configs/active.yaml">python/configs/active.yaml</option>
            <option value="python/configs/omega_base.yaml">python/configs/omega_base.yaml</option>
            <option value="python/configs/omega_experiment_01.yaml">python/configs/omega_experiment_01.yaml</option>
            <option value="python/configs/omega_loop_test.yaml">python/configs/omega_loop_test.yaml</option>
          </select>
        </div>
        <div style="width:140px;">
          <label>Max rounds</label>
          <input id="max_rounds" type="number" min="1" value="3" />
        </div>
        <div style="width:180px;">
          <label>Use Ollama</label>
          <select id="use_ollama">
            <option value="0">Off</option>
            <option value="1">On</option>
          </select>
        </div>
        <div style="flex:1 1 260px;">
          <label>Primary model</label>
          <div class="row" style="align-items:end;">
            <div style="flex:1 1 180px;">
              <select id="ollama_model"></select>
            </div>
            <div style="width:120px;">
              <button type="button" onclick="refreshModels()">Refresh</button>
            </div>
          </div>
        </div>
        <div style="flex:1 1 300px;">
          <label>Fallback models</label>
          <select id="ollama_models" multiple></select>
        </div>
      </div>
      <div class="row">
        <button class="primary" onclick="startLoop()">Start</button>
        <button class="danger" onclick="stopLoop()">Stop</button>
        <button onclick="refreshAll()">Refresh</button>
      </div>
      <div class="muted" id="models_hint">Loading Ollama models...</div>

      <div class="split">
        <div>
          <h3>Status</h3>
          <pre id="status">Loading...</pre>
        </div>
        <div>
          <h3>Models</h3>
          <pre id="models">Loading...</pre>
        </div>
      </div>

      <div>
        <h3>Recent Logs</h3>
        <pre id="logs">Loading...</pre>
      </div>
    </section>

    <section class="card grid">
      <div class="row">
        <div style="flex:1 1 260px;">
          <label>File preview</label>
          <select id="file_path" onchange="loadFile()">
            {% for item in file_candidates %}
            <option value="{{ item }}">{{ item }}</option>
            {% endfor %}
          </select>
        </div>
        <div style="align-self:end;">
          <button onclick="loadFile()">Load file</button>
        </div>
      </div>
      <div>
        <h3>File Content</h3>
        <pre class="file-box" id="file_content">Select a file.</pre>
      </div>
    </section>
  </main>

  <script>
    let cachedModels = [];

    function setSelectOptions(selectId, models, selectedValue) {
      const select = document.getElementById(selectId);
      const values = Array.isArray(selectedValue) ? selectedValue : [selectedValue].filter(Boolean);
      select.innerHTML = '';
      if (!models.length) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No models found';
        select.appendChild(option);
        return;
      }
      for (const model of models) {
        const option = document.createElement('option');
        option.value = model.name;
        const size = model.size ? ` • ${Math.round(model.size / 1024 / 1024)} MB` : '';
        const modified = model.modified_at ? ` • ${new Date(model.modified_at).toLocaleString()}` : '';
        option.textContent = `${model.name}${size}${modified}`;
        if (values.includes(model.name)) {
          option.selected = true;
        }
        select.appendChild(option);
      }
      if (!select.multiple && !select.value && models[0]) {
        select.value = models[0].name;
      }
    }

    async function refreshStatus() {
      const res = await fetch('/status');
      document.getElementById('status').textContent = JSON.stringify(await res.json(), null, 2);
    }
    async function refreshLogs() {
      const res = await fetch('/logs?limit=20');
      document.getElementById('logs').textContent = JSON.stringify(await res.json(), null, 2);
    }
    async function refreshModels() {
      const res = await fetch('/models');
      const payload = await res.json();
      cachedModels = Array.isArray(payload.models) ? payload.models : [];
      const currentPrimary = document.getElementById('ollama_model').value;
      const currentFallback = Array.from(document.getElementById('ollama_models').selectedOptions).map((option) => option.value);
      setSelectOptions('ollama_model', cachedModels, currentPrimary);
      setSelectOptions('ollama_models', cachedModels, currentFallback);
      document.getElementById('models').textContent = JSON.stringify(payload, null, 2);
      const hint = payload.error ? `Ollama model refresh failed: ${payload.error}` : `Found ${cachedModels.length} model(s) from /api/tags.`;
      document.getElementById('models_hint').textContent = hint;
    }
    async function refreshAll() {
      await Promise.all([refreshStatus(), refreshLogs(), refreshModels()]);
    }
    async function loadFile() {
      const path = document.getElementById('file_path').value;
      const res = await fetch('/file?path=' + encodeURIComponent(path));
      document.getElementById('file_content').textContent = await res.text();
    }
    async function startLoop() {
      const primarySelect = document.getElementById('ollama_model');
      const fallbackSelect = document.getElementById('ollama_models');
      const fallbackModels = Array.from(fallbackSelect.selectedOptions).map((option) => option.value);
      const selectedPrimary = primarySelect.value || (cachedModels[0] ? cachedModels[0].name : 'qwen-coder-3b-cpu:latest');
      const payload = {
        config_path: document.getElementById('config_path').value,
        max_rounds: parseInt(document.getElementById('max_rounds').value || '3', 10),
        use_ollama: document.getElementById('use_ollama').value === '1',
        ollama_model: selectedPrimary.trim(),
        ollama_models: fallbackModels.join(',')
      };
      const res = await fetch('/start', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      alert(JSON.stringify(await res.json(), null, 2));
      refreshAll();
    }
    async function stopLoop() {
      const res = await fetch('/stop', {method:'POST'});
      alert(JSON.stringify(await res.json(), null, 2));
      refreshAll();
    }
    refreshAll();
    loadFile();
    setInterval(refreshAll, 2000);
  </script>
</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(INDEX_HTML, file_candidates=_file_preview_candidates())


@app.get("/status")
def status():
    payload = _read_json(STATUS_PATH)
    with _process_lock:
        running = _current_process is not None and _current_process.poll() is None
        pid = _current_process.pid if running and _current_process else None
    payload.setdefault("running", running)
    payload["process_pid"] = pid
    payload["stop_flag_present"] = STOP_FLAG.exists()
    return jsonify(payload)


@app.get("/logs")
def logs():
    limit = int(request.args.get("limit", "25"))
    return jsonify(_tail_jsonl(LOG_PATH, limit=max(1, min(limit, 200))))


@app.get("/models")
def models():
    try:
        return jsonify({"models": list_ollama_models()})
    except Exception as exc:
        return jsonify({"models": [], "error": str(exc)})


@app.get("/file")
def file_preview():
    path = request.args.get("path", "")
    if not path:
        abort(400, description="Missing path")
    resolved = _allowed_file(path)
    return resolved.read_text(encoding="utf-8")


@app.post("/start")
def start():
    payload = request.get_json(force=True, silent=True) or {}
    config_path = str(payload.get("config_path") or "python/configs/active.yaml")
    max_rounds = int(payload.get("max_rounds") or 3)
    use_ollama = bool(payload.get("use_ollama"))
    result = _start_loop_process(
        config_path,
        max_rounds,
        use_ollama,
        ollama_model=str(payload.get("ollama_model") or "").strip() or None,
        ollama_models=str(payload.get("ollama_models") or "").strip() or None,
    )
    return jsonify(result)


@app.post("/stop")
def stop():
    return jsonify(_stop_loop_process())


def create_app() -> Flask:
    return app
