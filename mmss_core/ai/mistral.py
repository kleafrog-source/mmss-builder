import os
from mistralai import Mistral, MistralError

class MistralAPIError(Exception):
    """Custom exception for Mistral API errors."""
    pass

class MistralNeMoAPI:
    def __init__(self, model: str = None):
        """
        Initializes the MistralNeMoAPI client.
        
        Args:
            model (str): The name of the Mistral model to use. If not provided,
                         it uses the MISTRAL_MODEL environment variable, or defaults
                         to "mistral-large-latest".
        
        Raises:
            ValueError: If the MISTRAL_API_KEY environment variable is not set.
        """
        self.api_key = os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set.")

        self.client = Mistral(api_key=self.api_key)
        self.model = model or os.environ.get("MISTRAL_MODEL", "mistral-large-latest")

    def get_response(self, question: str, history: list = None) -> str:
        """
        Gets a response from the Mistral model.

        Args:
            question (str): The user's question.
            history (list, optional): A list of previous messages in the conversation. 
                                      Defaults to None.

        Returns:
            str: The content of the AI's response.
            
        Raises:
            MistralAPIError: If there is an error communicating with the Mistral API.
        """
        if history is None:
            history = []

        messages = history + [{"role": "user", "content": question}]

        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=messages,
            )
            # Проверка структуры ответа
            if hasattr(chat_response, 'choices') and len(chat_response.choices) > 0:
                return chat_response.choices[0].message.content
            else:
                raise MistralAPIError("Unexpected response format from Mistral API")
        except MistralError as e:
            # Catching the specific exception from the library is better
            raise MistralAPIError(f"An error occurred with the Mistral API: {e}") from e
        except Exception as e:
            # Catch any other unexpected errors
            raise MistralAPIError(f"An unexpected error occurred: {e}") from e

# Example usage (for testing, can be commented out)
if __name__ == '__main__':
    # Make sure to set the MISTRAL_API_KEY environment variable before running
    try:
        mistral_api = MistralNeMoAPI()

        # Test 1: Simple question
        print("--- Test 1: Simple Question ---")
        simple_question = "What is the capital of France?"
        simple_response = mistral_api.get_response(simple_question)
        print(f"Q: {simple_question}")
        print(f"A: {simple_response}")

        # Test 2: Question with history
        print("\n--- Test 2: Conversation with History ---")
        conversation_history = [
            {"role": "user", "content": "My name is Alex."},
            {"role": "assistant", "content": "Nice to meet you, Alex! How can I help you today?"}
        ]
        follow_up_question = "What is my name?"
        history_response = mistral_api.get_response(follow_up_question, history=conversation_history)
        print(f"History: {conversation_history}")
        print(f"Q: {follow_up_question}")
        print(f"A: {history_response}")

    except (ValueError, MistralAPIError) as e:
        print(e)