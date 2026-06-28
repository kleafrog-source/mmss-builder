import json

from mmss_core.ai.ollama import LocalOllamaAPI, OllamaAPIError


class MMSOrchestrator:
    def __init__(
        self,
        config_path='D:\\project\\mmss_core\\config\\mmss-orchestrator.json',
        model=None,
        base_url="http://127.0.0.1:11434",
        timeout_seconds=600,
    ):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.ollama_api = LocalOllamaAPI(model=model, base_url=base_url, timeout_seconds=timeout_seconds)
        self.ollama_api_error = None
        try:
            self.ollama_api.ping()
            print("[OK] Ollama initialized successfully for Orchestrator.")
        except OllamaAPIError as e:
            self.ollama_api_error = str(e)
            print(f"[WARN] Error initializing Ollama for Orchestrator: {self.ollama_api_error}")

    def get_agents(self):
        return self.config.get('agents', [])

    def generate_prompt(self, agent, question):
        output_template = agent.get('output_template', 'markdown')

        prompt = (
            f"Вы — агент MMSS: {agent['name']}\n"
            f"Оператор: {agent['operator']}\n"
            f"Цель: {agent['purpose']}\n"
            f"Мышление: {agent['thinking_style']}\n"
            f"Формат вывода: {output_template}\n\n"
            f"Вопрос: {question}\n\n"
            "ОЧЕНЬ ВАЖНО:\n"
        )

        if "nodeflow" in output_template:
            prompt += "- Ваш ответ ДОЛЖЕН быть строго в формате ```nodeflow-list ... ```\n"
        elif "dataview" in output_template:
            prompt += "- Ответ должен быть в формате Obsidian Markdown с frontmatter и dataview.\n"
        elif "linked-summary" in output_template:
            prompt += "- Ответ: 1-2 предложения с внутренними ссылками вида [[...]].\n"

        prompt += "- В конце добавьте строку: --- METRICS: {\"V\": 0.99, \"N\": 0.98, ...}\n"
        prompt += "- ВСЁ на русском языке, кроме технических идентификаторов.\n"
        return prompt

    def send_prompt_to_ollama(self, prompt):
        if self.ollama_api_error:
            raise OllamaAPIError(self.ollama_api_error)
        return self.ollama_api.get_response(prompt)
