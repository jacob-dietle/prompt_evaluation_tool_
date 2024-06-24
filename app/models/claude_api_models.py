from typing import List, Optional
from pydantic import BaseModel

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

    def dict(self):
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens
        }

class TextBlock(BaseModel):
    text: str
    type: str

class ClaudeResponse(BaseModel):
    id: str
    content: List[TextBlock]
    model: str
    role: str
    stop_reason: str
    stop_sequence: Optional[str]
    type: str
    usage: Usage