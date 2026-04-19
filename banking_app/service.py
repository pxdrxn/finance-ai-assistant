from __future__ import annotations

from pathlib import Path
from typing import Optional

from banking_app.models import ContaCorrente, Deposito, PessoaFisica, Saque
from banking_app.repository import BankingRepository


class BankingSystem:
    """
    Sistema bancário aderente ao diagrama UML, com alguns extras de demonstração.
    """

    def __init__(self, repository_path: Optional[Path] = None) -> None:
        self.repository = BankingRepository(
            repository_path or Path("data") / "banking_state.json"
        )
        self.clientes = self.repository.load()

    def salvar(self) -> None:
        self.repository.save(self.clientes)

    def criar_cliente(
        self, *, nome: str, data_nascimento: str, cpf: str, endereco: str
    ) -> tuple[bool, str]:
        if self.filtrar_cliente(cpf):
            return False, "Já existe cliente com esse CPF."

        cliente = PessoaFisica(
            nome=nome,
            data_nascimento=data_nascimento,
            cpf=cpf,
            endereco=endereco,
        )
        self.clientes.append(cliente)
        self.salvar()
        return True, "Cliente criado com sucesso."

    def criar_conta_corrente(self, cpf: str) -> tuple[bool, str]:
        cliente = self.filtrar_cliente(cpf)
        if not cliente:
            return False, "Cliente não encontrado."

        numero_conta = self._proximo_numero_conta()
        conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
        cliente.adicionar_conta(conta)
        self.salvar()
        return True, f"Conta criada com sucesso. Agência: {conta.agencia} | Conta: {conta.numero}"

    def depositar(self, cpf: str, numero_conta: int, valor: float) -> tuple[bool, str]:
        conta = self.buscar_conta(cpf, numero_conta)
        if not conta:
            return False, "Conta não encontrada para o CPF informado."

        sucesso = conta.cliente.realizar_transacao(conta, Deposito(valor))
        if sucesso:
            self.salvar()
            return True, f"Depósito de R$ {valor:.2f} realizado com sucesso."
        return False, "Não foi possível realizar o depósito."

    def sacar(self, cpf: str, numero_conta: int, valor: float) -> tuple[bool, str]:
        conta = self.buscar_conta(cpf, numero_conta)
        if not conta:
            return False, "Conta não encontrada para o CPF informado."

        sucesso = conta.cliente.realizar_transacao(conta, Saque(valor))
        if sucesso:
            self.salvar()
            return True, f"Saque de R$ {valor:.2f} realizado com sucesso."

        if valor > conta.limite:
            return False, "Operação falhou: o valor do saque excede o limite da conta."
        if valor <= 0:
            return False, "Operação falhou: o valor do saque deve ser positivo."
        if valor > conta.saldo:
            return False, "Operação falhou: saldo insuficiente."
        return False, "Operação falhou: número máximo de saques excedido."

    def transferir(
        self,
        cpf_origem: str,
        conta_origem_numero: int,
        cpf_destino: str,
        conta_destino_numero: int,
        valor: float,
    ) -> tuple[bool, str]:
        conta_origem = self.buscar_conta(cpf_origem, conta_origem_numero)
        conta_destino = self.buscar_conta(cpf_destino, conta_destino_numero)

        if not conta_origem or not conta_destino:
            return False, "Conta de origem ou destino não encontrada."

        if valor <= 0:
            return False, "O valor da transferência deve ser positivo."

        if not conta_origem.sacar(valor):
            return False, "Transferência não realizada por falta de saldo, limite ou quantidade de saques."

        conta_destino.depositar(valor)
        conta_origem.historico.adicionar_evento("Transferência enviada", valor)
        conta_destino.historico.adicionar_evento("Transferência recebida", valor)
        self.salvar()
        return True, f"Transferência de R$ {valor:.2f} realizada com sucesso."

    def gerar_extrato(self, cpf: str, numero_conta: int) -> tuple[bool, str]:
        conta = self.buscar_conta(cpf, numero_conta)
        if not conta:
            return False, "Conta não encontrada para o CPF informado."

        extrato = (
            "\n================ EXTRATO ================\n"
            f"Cliente: {conta.cliente.nome}\n"
            f"Agência: {conta.agencia}\n"
            f"Conta: {conta.numero}\n"
            "-----------------------------------------\n"
            f"{conta.historico.gerar_extrato()}\n"
            "-----------------------------------------\n"
            f"Saldo atual: R$ {conta.saldo:.2f}\n"
            "========================================="
        )
        return True, extrato

    def listar_clientes(self) -> str:
        if not self.clientes:
            return "Nenhum cliente cadastrado."

        linhas = []
        for cliente in self.clientes:
            linhas.append(
                f"Nome: {cliente.nome} | CPF: {cliente.cpf} | Contas: {len(cliente.contas)}"
            )
        return "\n".join(linhas)

    def listar_contas(self) -> str:
        contas = []
        for cliente in self.clientes:
            for conta in cliente.contas:
                contas.append(
                    f"Agência: {conta.agencia} | Conta: {conta.numero} | Titular: {cliente.nome} | Saldo: R$ {conta.saldo:.2f}"
                )
        return "\n".join(contas) if contas else "Nenhuma conta cadastrada."

    def buscar_conta(self, cpf: str, numero_conta: int) -> Optional[ContaCorrente]:
        cliente = self.filtrar_cliente(cpf)
        if not cliente:
            return None

        for conta in cliente.contas:
            if conta.numero == numero_conta and isinstance(conta, ContaCorrente):
                return conta
        return None

    def filtrar_cliente(self, cpf: str) -> Optional[PessoaFisica]:
        for cliente in self.clientes:
            if cliente.cpf == cpf:
                return cliente
        return None

    def _proximo_numero_conta(self) -> int:
        numeros = [conta.numero for cliente in self.clientes for conta in cliente.contas]
        return max(numeros, default=0) + 1
