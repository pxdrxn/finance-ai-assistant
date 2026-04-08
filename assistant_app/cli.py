from assistant_app.services.assistant import FinanceAssistant
from assistant_app.utils.logging_config import configure_logging


def main() -> None:
    configure_logging()
    assistant = FinanceAssistant(session_id="console")

    print("Assistente Virtual de Relacionamento Financeiro")
    print("Digite sua pergunta ou 'sair' para encerrar.")
    print("Exemplos:")
    print("- Meu nome é Carla e quero começar com R$ 3.000")
    print("- Qual a diferença entre CDB, poupança e Tesouro Selic?")
    print("- Se eu investir R$ 5.000 a 1,1% ao mês por 12 meses, quanto terei no final?")
    print("- Lembre qual foi o último valor que eu mencionei")

    while True:
        user_message = input("\nVocê: ").strip()
        if user_message.lower() in {"sair", "exit", "quit"}:
            print("\nAssistente: Até logo!")
            break
        resposta = assistant.responder(user_message)
        print(f"\nAssistente: {resposta}")
