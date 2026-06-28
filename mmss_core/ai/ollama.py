import json
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
        message = response.get("message") or {}
        content = message.get("content", "")
        if not content:
            raise OllamaAPIError("Empty response from Ollama.")
        return content

    def stream_response(self, question: str, history: Optional[list[dict[str, Any]]] = None, model: Optional[str] = None):
        selected_model = model or self.model
        if not selected_model:
            raise OllamaAPIError("Ollama model is not configured.")

        messages = (history or []) + [{"role": "user", "content": question}]
        payload = {
            "model": selected_model,
            "messages": messages,
            "stream": True,
        }
        for event in self._request_stream("POST", "/api/chat", payload):
            message = event.get("message") or {}
            content = message.get("content")
            if content:
                yield content

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
            raise OllamaAPIError(f"Ollama HTTP {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise OllamaAPIError(f"Ollama is unavailable at {self.base_url}: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise OllamaAPIError("Invalid JSON response from Ollama.") from exc
        except Exception as exc:
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
                    except json.JSONDecodeError as exc:
                        raise OllamaAPIError("Invalid JSON stream response from Ollama.") from exc
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise OllamaAPIError(f"Ollama HTTP {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise OllamaAPIError(f"Ollama is unavailable at {self.base_url}: {exc.reason}") from exc
        except Exception as exc:
            raise OllamaAPIError(f"Unexpected Ollama error: {exc}") from exc
