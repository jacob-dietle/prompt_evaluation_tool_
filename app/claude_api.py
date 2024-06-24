import os
import json
import logging
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from .models.claude_api_models import TextBlock, Usage

load_dotenv()

class ClaudeAPIClient:
    def __init__(self, api_key=None, model=None, max_tokens=1024, temperature=0.5):
        if api_key is None:
            api_key = os.getenv("CLAUDE_API_KEY")
        if api_key is None:
            raise ValueError("API key must be provided or set as environment variable ANTHROPIC_API_KEY")

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.last_token_usage = 0

    async def generate_response(self, prompt, model_parameters=None, additional_prefill=None):
        if model_parameters is None:
            model_parameters = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }

        model = model_parameters.get("model")
        logging.info(f"Model: {model}")
        max_tokens = model_parameters.get("max_tokens", self.max_tokens)
        temperature = model_parameters.get("temperature", self.temperature)

        if model is None:
            raise ValueError("Model must be provided either during initialization or in the model_parameters")

        logging.info(f"Generating response using model: {model}")
        prefill = '{"response": "'
        if additional_prefill:
            prefill = f'{{"response": "{additional_prefill}'

        # Create a new list with the existing messages and the additional prefill message
        updated_messages = [{"role": "user", "content": prompt}] + [{"role": "assistant", "content": prefill}]

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=updated_messages,
                temperature=temperature,
            )
        except Exception as e:
            logging.error(f"Error occurred while generating response from Claude API: {str(e)}")
            raise Exception(f"Claude API error: {str(e)}")

        # Get the token usage from the response and store it
        input_tokens = response.usage.input_tokens
        logging.info(f"Input Tokens: {input_tokens}")
        output_tokens = response.usage.output_tokens
        logging.info(f"Output Tokens: {output_tokens}")
        total_tokens = input_tokens + output_tokens
        self.last_token_usage = total_tokens

        # Extract the generated content from the response
        generated_content = ''.join([block.text for block in response.content])

        logging.info(f"Generated content: {generated_content[:10]}{'...' if len(generated_content) > 10 else ''}")

        return {
            "id": response.id,
            "content": [TextBlock(**block.dict()) for block in response.content],
            "model": response.model,
            "role": response.role,
            "stop_reason": response.stop_reason,
            "stop_sequence": response.stop_sequence,
            "type": response.type,
            "usage": Usage(**response.usage.dict()),
            "generated_content": generated_content
        }

    def get_token_usage(self):
        return self.last_token_usage
