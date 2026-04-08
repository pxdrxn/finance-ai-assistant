import logging
import re
from typing import Dict, Optional

from assistant_app.config import DEFAULT_CONTEXT_FILE, DEFAULT_MODEL
from assistant_app.core.calculations import calcular_juros_compostos, calcular_juros_simples
from assistant_app.core.text import DISCLAIMER, normalizar_texto
from assistant_app.services.context_store import JSONContextStore
from assistant_app.services.llm_service import LLMService


class FinanceAssistant:
    """
    Orquestra FAQ, cálculos, memória de contexto e integração com LLM.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        session_id: str = "default",
        context_store: Optional[JSONContextStore] = None,
        llm_service: Optional[LLMService] = None,
    ) -> None:
        self.session_id = session_id
        self.context_store = context_store or JSONContextStore(DEFAULT_CONTEXT_FILE)
        self.llm_service = llm_service or LLMService(model=model)
        self.logger = logging.getLogger(__name__)
        self.faq_base = {
            "cdb vs poupanca": (
                "Em geral, o CDB costuma oferecer rentabilidade maior do que a poupança, "
                "mas pode ter prazos, liquidez e regras de resgate diferentes. "
                "A poupança tende a ser mais simples e previsível, enquanto o CDB exige olhar "
                "taxa, emissor, prazo e cobertura do FGC."
            ),
            "o que e cdb": (
                "CDB é um Certificado de Depósito Bancário. Na prática, você empresta dinheiro "
                "ao banco e recebe uma remuneração conforme a taxa contratada."
            ),
            "o que e poupanca": (
                "Poupança é uma modalidade tradicional de reserva financeira, com liquidez simples "
                "e regras de rendimento definidas, embora normalmente renda menos que outras alternativas."
            ),
            "liquidez": (
                "Liquidez representa a facilidade de transformar um investimento em dinheiro disponível, "
                "com pouca perda de valor e em pouco tempo."
            ),
        }

    @property
    def user_context(self) -> Dict[str, Optional[float]]:
        return self.context_store.get_session(self.session_id)

    def responder(self, user_message: str) -> str:
        self.context_store.append_message(self.session_id, "user", user_message)
        self._update_context(user_message)
        normalized = normalizar_texto(user_message)

        if any(chave in normalized for chave in ["juros simples", "juros compostos", "simular", "simulacao"]):
            resposta = self._responder_calculo(user_message)
        elif any(chave in normalized for chave in ["quem sou eu", "qual meu nome", "lembra meu nome"]):
            resposta = self._responder_nome()
        elif any(chave in normalized for chave in ["qual valor eu falei", "ultimo valor", "lembra o valor"]):
            resposta = self._responder_ultimo_valor()
        else:
            resposta = self._responder_faq_ou_llm(user_message)

        resposta_final = self._adicionar_disclaimer(resposta)
        self.context_store.append_message(self.session_id, "assistant", resposta_final)
        return resposta_final

    def _responder_calculo(self, texto: str) -> str:
        parametros = self._extrair_parametros_calculo(texto)
        if not parametros:
            nome = self.user_context.get("name")
            prefixo = f"{nome}, " if nome else ""
            return (
                f"{prefixo}para fazer a simulação, informe capital, taxa e tempo. "
                "Exemplo: 'simular juros compostos para R$ 1000 a 1,2% por 12 meses'."
            )

        tipo = parametros["tipo"]
        capital = parametros["capital"]
        taxa = parametros["taxa"]
        tempo = parametros["tempo"]

        if tipo == "simples":
            resultado = calcular_juros_simples(capital, taxa, tempo)
            return self._formatar_resultado("simples", resultado)

        resultado = calcular_juros_compostos(capital, taxa, tempo)
        return self._formatar_resultado("compostos", resultado)

    def _responder_nome(self) -> str:
        nome = self.user_context.get("name")
        if nome:
            return f"Seu nome registrado no contexto é {nome}."
        return "Ainda não recebi seu nome. Se quiser, diga algo como: meu nome é Ana."

    def _responder_ultimo_valor(self) -> str:
        ultimo_valor = self.user_context.get("last_amount")
        if ultimo_valor is not None:
            return f"O último valor que você mencionou foi R$ {ultimo_valor:.2f}."
        return "Ainda não identifiquei nenhum valor anterior na conversa."

    def _responder_faq_ou_llm(self, pergunta: str) -> str:
        resposta_local = self._responder_faq_local(pergunta)
        saudacao = self._saudacao_contextual()

        if not self.llm_service.is_available:
            if resposta_local:
                return f"{saudacao}{resposta_local}"
            return (
                f"{saudacao}No momento estou sem integração ativa com a API do modelo. "
                "Posso responder perguntas básicas sobre CDB, poupança, liquidez e fazer simulações financeiras."
            )

        system_prompt = (
            "Você é um Assistente Virtual de Relacionamento Financeiro. "
            "Responda em português do Brasil, com clareza, educação e linguagem acessível. "
            "Explique conceitos de forma educativa e neutra. "
            "Nunca forneça recomendação personalizada de investimento. "
            "Se a pergunta sair do escopo financeiro, responda de forma breve e redirecione para o tema financeiro."
        )

        user_prompt = (
            f"Contexto conhecido: {self._resumir_contexto()}\n"
            f"Histórico recente: {self._historico_recente()}\n"
            f"Base local relevante: {resposta_local or 'Sem resposta local específica.'}\n"
            f"Pergunta do usuário: {pergunta}"
        )

        resposta_llm = self.llm_service.generate_answer(system_prompt, user_prompt)
        if resposta_llm:
            return f"{saudacao}{resposta_llm}"

        self.logger.warning("Usando fallback local após falha do provedor de LLM.")
        if resposta_local:
            return (
                f"{saudacao}{resposta_local} "
                "Tive uma instabilidade momentânea ao consultar o modelo, então respondi com a base local."
            )
        return (
            f"{saudacao}Tive uma instabilidade momentânea ao consultar o modelo. "
            "Você pode tentar novamente ou me pedir uma simulação de juros."
        )

    def _update_context(self, user_message: str) -> None:
        nome_match = re.search(
            r"\b(meu nome e|meu nome é|me chamo|sou o|sou a)\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s'-]{1,40})",
            user_message,
            re.IGNORECASE,
        )

        nome = nome_match.group(2).strip().title() if nome_match else None
        valor = self._extrair_capital(user_message)

        if valor is None:
            normalized = normalizar_texto(user_message)
            if any(chave in normalized for chave in ["tenho", "valor", "capital", "investir", "guardar"]):
                valor_match = re.search(
                    r"(\d+(?:\.\d{3})*(?:,\d+)?|\d+(?:[.,]\d+)?)(?!\s*%)",
                    user_message,
                    re.IGNORECASE,
                )
                if valor_match and any(char.isdigit() for char in valor_match.group(1)):
                    valor_br = valor_match.group(1).replace(".", "").replace(",", ".")
                    try:
                        valor = float(valor_br)
                    except ValueError:
                        valor = None

        self.context_store.update_context(self.session_id, name=nome, last_amount=valor)

    def _responder_faq_local(self, pergunta: str) -> Optional[str]:
        pergunta_normalizada = normalizar_texto(pergunta)

        for chave, resposta in self.faq_base.items():
            if chave in pergunta_normalizada:
                return resposta

        if "cdb" in pergunta_normalizada and "poupanca" in pergunta_normalizada:
            return self.faq_base["cdb vs poupanca"]
        return None

    def _extrair_parametros_calculo(self, texto: str) -> Optional[Dict[str, float]]:
        texto_normalizado = normalizar_texto(texto)
        tipo = "composto" if "composto" in texto_normalizado else "simples"

        taxa_match = re.search(r"(\d+(?:[.,]\d+)?)\s*%", texto, re.IGNORECASE)
        tempo_match = re.search(r"(\d+)\s*(mes|meses|ano|anos)", texto, re.IGNORECASE)
        capital = self._extrair_capital(texto)
        taxa = float(taxa_match.group(1).replace(",", ".")) if taxa_match else None
        tempo = int(tempo_match.group(1)) if tempo_match else None

        if capital is None and self.user_context.get("last_amount") is not None:
            capital = float(self.user_context["last_amount"])

        if not all([capital is not None, taxa is not None, tempo is not None]):
            return None

        return {
            "tipo": tipo,
            "capital": capital,
            "taxa": taxa,
            "tempo": tempo,
        }

    def _extrair_capital(self, texto: str) -> Optional[float]:
        padroes = [
            r"(?:r\$\s*)(\d+(?:\.\d{3})*(?:,\d+)?|\d+(?:[.,]\d+)?)",
            r"(?:capital\s+de\s+)(\d+(?:\.\d{3})*(?:,\d+)?|\d+(?:[.,]\d+)?)",
            r"(?:valor\s+de\s+)(\d+(?:\.\d{3})*(?:,\d+)?|\d+(?:[.,]\d+)?)",
        ]
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                valor = match.group(1).replace(".", "").replace(",", ".")
                try:
                    return float(valor)
                except ValueError:
                    continue
        return None

    def _formatar_resultado(self, tipo: str, resultado: Dict[str, float]) -> str:
        nome = self.user_context.get("name")
        prefixo = f"{nome}, " if nome else ""
        return (
            f"{prefixo}a simulação de juros {tipo} ficou assim:\n"
            f"- Capital inicial: R$ {resultado['capital']:.2f}\n"
            f"- Taxa: {resultado['taxa_percentual']:.2f}% por período\n"
            f"- Tempo: {resultado['tempo']} períodos\n"
            f"- Juros totais: R$ {resultado['juros']:.2f}\n"
            f"- Montante final: R$ {resultado['montante']:.2f}"
        )

    def _adicionar_disclaimer(self, texto: str) -> str:
        return f"{texto.strip()}{DISCLAIMER}"

    def _saudacao_contextual(self) -> str:
        nome = self.user_context.get("name")
        return f"{nome}, " if nome else ""

    def _resumir_contexto(self) -> str:
        nome = self.user_context.get("name")
        ultimo_valor = self.user_context.get("last_amount")
        partes = []
        if nome:
            partes.append(f"Nome do usuário: {nome}.")
        if ultimo_valor is not None:
            partes.append(f"Último valor mencionado: R$ {ultimo_valor:.2f}.")
        return " ".join(partes) if partes else "Nenhum contexto registrado."

    def _historico_recente(self) -> str:
        messages = self.user_context.get("messages", [])
        if not messages:
            return "Sem mensagens anteriores."
        return " | ".join(f"{item['role']}: {item['content']}" for item in messages[-6:])
