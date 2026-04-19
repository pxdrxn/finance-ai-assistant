from pathlib import Path
from uuid import uuid4

from banking_app.models import ContaCorrente, Deposito, PessoaFisica, Saque
from banking_app.service import BankingSystem


def build_cliente() -> PessoaFisica:
    return PessoaFisica(
        nome="Maria Silva",
        data_nascimento="01-01-1990",
        cpf="12345678900",
        endereco="Rua A, 10 - Centro - São Paulo/SP",
    )


def build_repository_path() -> Path:
    base_dir = Path("data")
    base_dir.mkdir(exist_ok=True)
    return base_dir / f"banking_test_{uuid4().hex}.json"


def test_deposito_registra_no_historico() -> None:
    cliente = build_cliente()
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=1)

    sucesso = cliente.realizar_transacao(conta, Deposito(250.0))

    assert sucesso is True
    assert conta.saldo == 250.0
    assert conta.historico.transacoes[0]["tipo"] == "Deposito"


def test_saque_respeita_limite_da_conta_corrente() -> None:
    cliente = build_cliente()
    conta = ContaCorrente(
        saldo=1000.0,
        numero=1,
        agencia="0001",
        cliente=cliente,
        limite=500.0,
        limite_saques=3,
    )

    sucesso = cliente.realizar_transacao(conta, Saque(600.0))

    assert sucesso is False
    assert conta.saldo == 1000.0


def test_transferencia_move_valores_entre_contas() -> None:
    sistema = BankingSystem(repository_path=build_repository_path())
    sistema.criar_cliente(
        nome="Maria Silva",
        data_nascimento="01-01-1990",
        cpf="12345678900",
        endereco="Rua A, 10 - Centro - São Paulo/SP",
    )
    sistema.criar_cliente(
        nome="João Souza",
        data_nascimento="02-02-1992",
        cpf="99999999999",
        endereco="Rua B, 20 - Centro - Rio de Janeiro/RJ",
    )
    sistema.criar_conta_corrente("12345678900")
    sistema.criar_conta_corrente("99999999999")
    sistema.depositar("12345678900", 1, 800.0)

    sucesso, _ = sistema.transferir("12345678900", 1, "99999999999", 2, 300.0)

    conta_origem = sistema.buscar_conta("12345678900", 1)
    conta_destino = sistema.buscar_conta("99999999999", 2)

    assert sucesso is True
    assert conta_origem is not None and conta_origem.saldo == 500.0
    assert conta_destino is not None and conta_destino.saldo == 300.0
