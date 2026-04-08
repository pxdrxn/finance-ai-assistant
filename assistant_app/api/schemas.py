from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Mensagem enviada pelo usuário.")
    session_id: Optional[str] = Field(default="default", description="Identificador da conversa.")


class ChatResponse(BaseModel):
    session_id: str
    answer: str


class HealthResponse(BaseModel):
    status: str
