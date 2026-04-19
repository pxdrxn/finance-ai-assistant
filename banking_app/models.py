from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


AGENCIA_PADRAO = "0001"


class Historico:
    def __init__(self) -> None:
        self._transacoes: list[dict[str, str | float]] = []

    @property
    def transacoes(self) -> list[dict[str, str | float]]:
        return self._transacoes

    def adicionar_transacao(self, transacao: "Transacao") -> None:
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

    def adicionar_evento(self, tipo: str, valor: float) -> None:
        self._transacoes.append(
            {
                "tipo": tipo,
                "valor": valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

    def gerar_extrato(self) -> str:
        if not self._transacoes:
            return "Não foram realizadas movimentações."

        linhas = []
        for item in self._transacoes:
            linhas.append(
                f"{item['data']} | {str(item['tipo']):<22} | R$ {float(item['valor']):.2f}"
            )
        return "\n".join(linhas)


class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta: "Conta") -> bool:
        raise NotImplementedError


@dataclass
class Deposito(Transacao):
    valor: float

    def registrar(self, conta: "Conta") -> bool:
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)
        return sucesso


@dataclass
class Saque(Transacao):
    valor: float

    def registrar(self, conta: "Conta") -> bool:
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)
        return sucesso


@dataclass
class Conta:
    saldo: float
    numero: int
    agencia: str
    cliente: "Cliente"
    historico: Historico = field(default_factory=Historico)

    @classmethod
    def nova_conta(cls, cliente: "Cliente", numero: int) -> "Conta":
        return cls(saldo=0.0, numero=numero, agencia=AGENCIA_PADRAO, cliente=cliente)

    def sacar(self, valor: float) -> bool:
        if valor <= 0:
            return False

        if valor > self.saldo:
            return False

        self.saldo -= valor
        return True

    def depositar(self, valor: float) -> bool:
        if valor <= 0:
            return False

        self.saldo += valor
        return True


@dataclass
class ContaCorrente(Conta):
    limite: float = 500.0
    limite_saques: int = 3

    @classmethod
    def nova_conta(cls, cliente: "Cliente", numero: int) -> "ContaCorrente":
        return cls(
            saldo=0.0,
            numero=numero,
            agencia=AGENCIA_PADRAO,
            cliente=cliente,
        )

    def sacar(self, valor: float) -> bool:
        numero_saques = len(
            [item for item in self.historico.transacoes if item["tipo"] == "Saque"]
        )

        if valor > self.limite:
            return False

        if numero_saques >= self.limite_saques:
            return False

        return super().sacar(valor)


@dataclass
class Cliente:
    endereco: str
    contas: list[Conta] = field(default_factory=list)

    def realizar_transacao(self, conta: Conta, transacao: Transacao) -> bool:
        return transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta) -> None:
        self.contas.append(conta)


@dataclass
class PessoaFisica(Cliente):
    cpf: str = ""
    nome: str = ""
    data_nascimento: str = ""
