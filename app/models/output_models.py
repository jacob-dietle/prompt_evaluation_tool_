from typing import List, Dict, Any
from .claude_api_models import Usage
from pydantic import BaseModel
import json


class OutputContent(BaseModel):
    variables: Dict[str, Any]  
    prompt: str
    response: str
    token_usage: Usage

    def __str__(self):
        return (
            f"Variables: {json.dumps(self.variables, indent=2)}\n"
            f"Prompt:\n{self.prompt}\n\n"
            f"Response:\n{self.response}\n\n"
            f"Token Usage: {json.dumps(self.token_usage.dict(), indent=2)}\n\n"
            "----------------------------------------\n\n"
        )
    
    def to_csv(self):
        def escape_csv(value):
            value = str(value)
            if ',' in value or '\n' in value:
                value = '"{}"'.format(value.replace('"', '""').replace('\n', r'\n'))
            return value
        variables_json = json.dumps(self.variables)
        prompt_escaped = escape_csv(self.prompt)
        response_escaped = escape_csv(self.response)

        return f"{escape_csv(variables_json)},{prompt_escaped},{response_escaped},{self.token_usage.input_tokens},{self.token_usage.output_tokens}"
    
    def to_dataframe(self):
        return {
            "Variables": json.dumps(self.variables),
            "Prompt": self.prompt,
            "Response": self.response,
            "Input Tokens": self.token_usage.input_tokens,
            "Output Tokens": self.token_usage.output_tokens
        }


