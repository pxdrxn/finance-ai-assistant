import logging

from fastapi import FastAPI

from assistant_app.api.schemas import ChatRequest, ChatResponse, HealthResponse
from assistant_app.services.assistant import FinanceAssistant
from assistant_app.utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Finance Relationship Assistant API",
    description="API para FAQ financeiro, memória de contexto e simulação de juros.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    logger.info("Nova mensagem recebida para session_id=%s", payload.session_id)
    assistant = FinanceAssistant(session_id=payload.session_id or "default")
    answer = assistant.responder(payload.message)
    return ChatResponse(session_id=payload.session_id or "default", answer=answer)
