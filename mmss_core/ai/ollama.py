import json
import socket
from typing import Any, Optional
from urllib import error, request


class OllamaAPIError(Exception):
    """Raised when the local Ollama API request fails."""


class LocalOllamaAPI:
    def __init__(
        self,
        model: Optional[str] = None,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: int = 480,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def ping(self) -> bool:
        self._request("GET", "/api/tags")
        return True

    def list_models(self) -> list[str]:
        response = self._request("GET", "/api/tags")
        models = response.get("models", [])
        return [model.get("name") for model in models if model.get("name")]

    def get_response(self, question: str, history: Optional[list[dict[str, Any]]] = None, model: Optional[str] = None) -> str:
        selected_model = model or self.model
        if not selected_model:
            raise OllamaAPIError("Ollama model is not configured.")

        messages = (history or []) + [{"role": "user", "content": question}]
        payload = {
            "model": selected_model,
            "messages": messages,
            "stream": False,
        }
        response = self._request("POST", "/api/chat", payload)
        text = self._compose_response_text(response)
        if text:
            return text
        return json.dumps(response, ensure_ascii=False)

    def stream_response(self, question: str, history: Optional[list[dict[str, Any]]] = None, model: Optional[str] = None):
        for event in self.stream_response_events(question, history=history, model=model):
            content = event.get("content")
            if content:
                yield content

    def stream_response_events(self, question: str, history: Optional[list[dict[str, Any]]] = None, model: Optional[str] = None):
        selected_model = model or self.model
        if not selected_model:
            raise OllamaAPIError("Ollama model is not configured.")

        messages = (history or []) + [{"role": "user", "content": question}]
        payload = {
            "model": selected_model,
            "messages": messages,
            "stream": True,
        }
        for raw_event in self._request_stream("POST", "/api/chat", payload):
            emitted = False
            for part in self._extract_text_parts(raw_event):
                emitted = True
                yield {
                    "type": part["kind"],
                    "content": part["text"],
                    "done": bool(raw_event.get("done")),
                }
            if not emitted and raw_event.get("done"):
                yield {"type": "done", "content": "", "done": True}

    def get_embedding(self, text: str, model: Optional[str] = None) -> list[float]:
        selected_model = model or self.model
        if not selected_model:
            raise OllamaAPIError("Ollama embedding model is not configured.")

        payload = {"model": selected_model, "input": text}
        try:
            response = self._request("POST", "/api/embed", payload)
            embeddings = response.get("embeddings") or []
            if embeddings and isinstance(embeddings[0], list):
                return embeddings[0]
        except OllamaAPIError:
            response = self._request("POST", "/api/embeddings", {"model": selected_model, "prompt": text})
            embedding = response.get("embedding")
            if embedding:
                return embedding
            raise

        raise OllamaAPIError("Empty embedding response from Ollama.")

    def _compose_response_text(self, payload: dict[str, Any]) -> str:
        parts = self._extract_text_parts(payload)
        if not parts:
            return ""
        return "".join(part["text"] for part in parts if part.get("text"))

    def _extract_text_parts(self, payload: dict[str, Any]) -> list[dict[str, str]]:
        parts: list[dict[str, str]] = []

        def add_part(kind: str, value: Any):
            if value is None:
                return
            text = str(value).strip()
            if not text:
                return
            if kind == "thinking":
                text = f"<think>\n{text}\n</think>\n"
            parts.append({"kind": kind, "text": text})

        message = payload.get("message")
        if isinstance(message, dict):
            add_part("thinking", message.get("thinking"))
            add_part("thinking", message.get("think"))
            add_part("thinking", message.get("reasoning"))
            add_part("content", message.get("content"))

        add_part("thinking", payload.get("thinking"))
        add_part("thinking", payload.get("think"))
        add_part("thinking", payload.get("reasoning"))
        add_part("content", payload.get("response"))
        add_part("content", payload.get("content"))

        return parts

    def _request(self, method: str, path: str, payload: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                if not raw:
                    return {}
                return json.loads(raw)
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            diagnostics = self._build_diagnostics(details)
            raise OllamaAPIError(f"Ollama HTTP {exc.code}: {details}{diagnostics}") from exc
        except error.URLError as exc:
            raise OllamaAPIError(f"Ollama is unavailable at {self.base_url}: {exc.reason}.{self._availability_diagnostics()}") from exc
        except json.JSONDecodeError as exc:
            raise OllamaAPIError("Invalid JSON response from Ollama. Possible causes: truncated response, proxy/body corruption, model crash.") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise OllamaAPIError(f"Ollama request timed out after {self.timeout_seconds}s.{self._timeout_diagnostics()}") from exc
        except Exception as exc:
            message = str(exc)
            if "timed out" in message.lower():
                raise OllamaAPIError(f"Unexpected Ollama timeout after {self.timeout_seconds}s.{self._timeout_diagnostics()}") from exc
            raise OllamaAPIError(f"Unexpected Ollama error: {exc}") from exc

    def _request_stream(self, method: str, path: str, payload: Optional[dict[str, Any]] = None):
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        yield {"response": line}
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            diagnostics = self._build_diagnostics(details)
            raise OllamaAPIError(f"Ollama HTTP {exc.code}: {details}{diagnostics}") from exc
        except error.URLError as exc:
            raise OllamaAPIError(f"Ollama is unavailable at {self.base_url}: {exc.reason}.{self._availability_diagnostics()}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise OllamaAPIError(f"Ollama stream timed out after {self.timeout_seconds}s.{self._timeout_diagnostics()}") from exc
        except Exception as exc:
            message = str(exc)
            if "timed out" in message.lower():
                raise OllamaAPIError(f"Unexpected Ollama stream timeout after {self.timeout_seconds}s.{self._timeout_diagnostics()}") from exc
            raise OllamaAPIError(f"Unexpected Ollama error: {exc}") from exc

    def _timeout_diagnostics(self) -> str:
        return " Likely causes: model is still generating, model too large for available RAM/VRAM, context too large, or Ollama is overloaded."

    def _availability_diagnostics(self) -> str:
        return " Check that Ollama is running, the base URL is correct, and the model is installed locally."

    def _build_diagnostics(self, details: str) -> str:
        lowered = (details or "").lower()
        hints = []
        if "context" in lowered or "token" in lowered:
            hints.append("context window or prompt too large")
        if "not found" in lowered or "model" in lowered:
            hints.append("selected model may be missing")
        if "memory" in lowered or "cuda" in lowered or "alloc" in lowered:
            hints.append("insufficient RAM/VRAM")
        if "truncate" in lowered or "unexpected end" in lowered:
            hints.append("response may have been truncated")
        if not hints:
            return ""
        return f" Possible causes: {', '.join(hints)}."
