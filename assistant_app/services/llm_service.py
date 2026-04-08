import logging
import os
from typing import Optional

from openai import OpenAI

from assistant_app.config import DEFAULT_MODEL


class LLMService:
    """
    Encapsula o acesso ao provedor de LLM e centraliza o tratamento de erros.
    """

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.logger = logging.getLogger(__name__)

    @property
    def is_available(self) -> bool:
        return self.client is not None

    def generate_answer(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if not self.client:
            return None

        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.output_text.strip()
        except Exception as exc:
            self.logger.warning("Falha ao consultar o modelo: %s", exc)
            return None
