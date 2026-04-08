from pathlib import Path
from uuid import uuid4

from assistant_app.services.assistant import FinanceAssistant
from assistant_app.services.context_store import JSONContextStore
from assistant_app.services.llm_service import LLMService


class StubLLMService(LLMService):
    def __init__(self) -> None:
        pass

    @property
    def is_available(self) -> bool:
        return False


def _build_store_path() -> Path:
    base_dir = Path("data")
    base_dir.mkdir(exist_ok=True)
    return base_dir / f"test_context_{uuid4().hex}.json"


def test_contexto_persiste_nome_e_valor() -> None:
    store = JSONContextStore(_build_store_path())
    assistant = FinanceAssistant(
        session_id="teste",
        context_store=store,
        llm_service=StubLLMService(),
    )

    assistant.responder("Meu nome é Carla")
    assistant.responder("Quero investir R$ 3500")

    session = store.get_session("teste")
    assert session["name"] == "Carla"
    assert session["last_amount"] == 3500.0


def test_usa_ultimo_valor_na_simulacao() -> None:
    store = JSONContextStore(_build_store_path())
    assistant = FinanceAssistant(
        session_id="teste",
        context_store=store,
        llm_service=StubLLMService(),
    )

    assistant.responder("Tenho R$ 2000")
    resposta = assistant.responder("Simular juros compostos a 1% por 12 meses")

    assert "Capital inicial: R$ 2000.00" in resposta
