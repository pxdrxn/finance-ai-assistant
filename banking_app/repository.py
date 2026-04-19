from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from banking_app.models import ContaCorrente, Historico, PessoaFisica


class BankingRepository:
    """
    Persistência simples em JSON para manter os dados entre execuções.
    """

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, clientes: list[PessoaFisica]) -> None:
        payload = {"clientes": [self._serialize_cliente(cliente) for cliente in clientes]}
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def load(self) -> list[PessoaFisica]:
        if not self.file_path.exists():
            return []

        with self.file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        clientes: list[PessoaFisica] = []
        for item in payload.get("clientes", []):
            cliente = PessoaFisica(
                nome=item["nome"],
                data_nascimento=item["data_nascimento"],
                cpf=item["cpf"],
                endereco=item["endereco"],
            )
            for conta_item in item.get("contas", []):
                historico = Historico()
                historico.transacoes.extend(conta_item.get("historico", []))
                conta = ContaCorrente(
                    saldo=conta_item["saldo"],
                    numero=conta_item["numero"],
                    agencia=conta_item["agencia"],
                    cliente=cliente,
                    historico=historico,
                    limite=conta_item.get("limite", 500.0),
                    limite_saques=conta_item.get("limite_saques", 3),
                )
                cliente.adicionar_conta(conta)
            clientes.append(cliente)
        return clientes

    def _serialize_cliente(self, cliente: PessoaFisica) -> dict[str, Any]:
        return {
            "nome": cliente.nome,
            "data_nascimento": cliente.data_nascimento,
            "cpf": cliente.cpf,
            "endereco": cliente.endereco,
            "contas": [
                {
                    "saldo": conta.saldo,
                    "numero": conta.numero,
                    "agencia": conta.agencia,
                    "limite": conta.limite,
                    "limite_saques": conta.limite_saques,
                    "historico": conta.historico.transacoes,
                }
                for conta in cliente.contas
                if isinstance(conta, ContaCorrente)
            ],
        }
