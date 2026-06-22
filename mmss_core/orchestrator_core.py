import json
from mmss_core.ai.mistral import MistralNeMoAPI, MistralAPIError
import os

class MMSOrchestrator:
    def __init__(self, config_path='D:\\project\\mmss_core\\config\\mmss-orchestrator.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.mistral_api = None
        self.mistral_api_error = None
        try:
            api_key = os.environ.get("MISTRAL_API_KEY")
            if api_key and api_key.strip() and api_key != "your_mistral_api_key_here":
                self.mistral_api = MistralNeMoAPI()
                print("[OK] Mistral API initialized successfully for Orchestrator.")
            else:
                self.mistral_api_error = "MISTRAL_API_KEY not set in .env file"
                print(f"[WARN] {self.mistral_api_error}")
        except Exception as e:
            self.mistral_api_error = str(e)
            print(f"[WARN] Error initializing Mistral API for Orchestrator: {self.mistral_api_error}")

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

    def send_prompt_to_mistral(self, prompt):
        """Send a pre-built prompt to Mistral API."""
        if not self.mistral_api:
            raise MistralAPIError(self.mistral_api_error or "Mistral API not initialized.")
        
        response = self.mistral_api.get_response(prompt)
        return response