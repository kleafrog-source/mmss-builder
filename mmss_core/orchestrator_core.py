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
                print("✓ Mistral API initialized successfully for Orchestrator.")
            else:
                self.mistral_api_error = "MISTRAL_API_KEY not set in .env file"
                print(f"⚠ {self.mistral_api_error}")
        except Exception as e:
            self.mistral_api_error = str(e)
            print(f"⚠ Error initializing Mistral API for Orchestrator: {self.mistral_api_error}")

    def get_agents(self):
        return self.config.get('agents', [])

    def generate_prompt(self, agent, question):
        system_prompt = f"MMSS Activation\n"
        system_prompt += f"Operator: {agent['operator']}\n"
        system_prompt += f"Purpose: {agent['purpose']}\n"
        system_prompt += f"Thinking Style: {agent['thinking_style']}\n"
        system_prompt += f"Question: {question}\n"
        system_prompt += "Format your answer as: ANSWER_TEXT --- METRICS: {...}"
        return system_prompt

    def send_prompt_to_mistral(self, prompt):
        if not self.mistral_api:
            raise MistralAPIError(self.mistral_api_error or "Mistral API not initialized.")
        
        response = self.mistral_api.get_response(prompt)
        return response
