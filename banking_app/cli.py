from banking_app.service import BankingSystem


MENU = """
================ MENU ================
[1] Criar cliente
[2] Criar conta corrente
[3] Depositar
[4] Sacar
[5] Extrato
[6] Listar clientes
[7] Listar contas
[8] Transferir entre contas
[0] Sair
======================================
=> """


def main() -> None:
    sistema = BankingSystem()

    print("Sistema Bancário Orientado a Objetos")
    print("Versão alinhada ao diagrama UML da DIO, com persistência local e extrato detalhado.")

    while True:
        opcao = input(MENU).strip()

        if opcao == "1":
            _criar_cliente(sistema)
        elif opcao == "2":
            _criar_conta(sistema)
        elif opcao == "3":
            _depositar(sistema)
        elif opcao == "4":
            _sacar(sistema)
        elif opcao == "5":
            _extrato(sistema)
        elif opcao == "6":
            print(f"\n{sistema.listar_clientes()}\n")
        elif opcao == "7":
            print(f"\n{sistema.listar_contas()}\n")
        elif opcao == "8":
            _transferir(sistema)
        elif opcao == "0":
            print("\nEncerrando o sistema. Até logo!")
            break
        else:
            print("\nOperação inválida. Selecione uma opção do menu.\n")


def _criar_cliente(sistema: BankingSystem) -> None:
    print("\nCadastro de cliente")
    nome = input("Nome completo: ").strip()
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ").strip()
    cpf = input("CPF (somente números): ").strip()
    endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ").strip()
    _, mensagem = sistema.criar_cliente(
        nome=nome,
        data_nascimento=data_nascimento,
        cpf=cpf,
        endereco=endereco,
    )
    print(f"\n{mensagem}\n")


def _criar_conta(sistema: BankingSystem) -> None:
    print("\nCriação de conta corrente")
    cpf = input("CPF do cliente: ").strip()
    _, mensagem = sistema.criar_conta_corrente(cpf)
    print(f"\n{mensagem}\n")


def _depositar(sistema: BankingSystem) -> None:
    print("\nDepósito")
    cpf = input("CPF do titular: ").strip()
    conta = int(input("Número da conta: ").strip())
    valor = float(input("Valor do depósito: ").replace(",", "."))
    _, mensagem = sistema.depositar(cpf, conta, valor)
    print(f"\n{mensagem}\n")


def _sacar(sistema: BankingSystem) -> None:
    print("\nSaque")
    cpf = input("CPF do titular: ").strip()
    conta = int(input("Número da conta: ").strip())
    valor = float(input("Valor do saque: ").replace(",", "."))
    _, mensagem = sistema.sacar(cpf, conta, valor)
    print(f"\n{mensagem}\n")


def _extrato(sistema: BankingSystem) -> None:
    print("\nExtrato")
    cpf = input("CPF do titular: ").strip()
    conta = int(input("Número da conta: ").strip())
    _, mensagem = sistema.gerar_extrato(cpf, conta)
    print(f"{mensagem}\n")


def _transferir(sistema: BankingSystem) -> None:
    print("\nTransferência")
    cpf_origem = input("CPF da conta de origem: ").strip()
    conta_origem = int(input("Número da conta de origem: ").strip())
    cpf_destino = input("CPF da conta de destino: ").strip()
    conta_destino = int(input("Número da conta de destino: ").strip())
    valor = float(input("Valor da transferência: ").replace(",", "."))
    _, mensagem = sistema.transferir(cpf_origem, conta_origem, cpf_destino, conta_destino, valor)
    print(f"\n{mensagem}\n")
