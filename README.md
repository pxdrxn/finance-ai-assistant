# Sistema Bancário Orientado a Objetos

Projeto em Python desenvolvido com base no modelo UML clássico do desafio da DIO. A aplicação implementa as entidades `Cliente`, `PessoaFisica`, `Conta`, `ContaCorrente`, `Historico`, `Transacao`, `Deposito` e `Saque`, com foco em orientação a objetos, clareza de modelagem e regras de negócio bancárias.

## Objetivo

Simular operações bancárias essenciais em um sistema de console, respeitando o relacionamento entre cliente, conta e transações conforme o diagrama da atividade.

## Modelagem implementada

- `Historico`: registra transações com data, tipo e valor
- `Transacao`: interface abstrata com método `registrar`
- `Deposito` e `Saque`: implementações concretas da interface
- `Cliente`: responsável por executar transações e vincular contas
- `PessoaFisica`: especialização de cliente com `cpf`, `nome` e `data_nascimento`
- `Conta`: classe base com `saldo`, `numero`, `agencia`, `cliente` e `historico`
- `ContaCorrente`: especialização com `limite` e `limite_saques`

## Extras adicionados

- persistência simples em JSON para manter clientes e contas entre execuções
- extrato detalhado com data e tipo de movimentação
- transferência entre contas no menu principal
- testes automatizados para regras críticas do domínio

## Estrutura

```text
banking_app/
  cli.py         # Interface de console
  models.py      # Classes do domínio bancário
  repository.py  # Persistência em JSON
  service.py     # Regras de orquestração do sistema
tests/
  test_banking_domain.py
```

## Como executar

```bash
python app.py
```

Ou:

```bash
python main.py
```

## Operações disponíveis

- criar cliente
- criar conta corrente
- depositar
- sacar
- emitir extrato
- listar clientes
- listar contas
- transferir entre contas

## Testes

```bash
pytest
```

## Exemplo de fluxo

1. Cadastrar um cliente com CPF único.
2. Criar uma conta corrente para esse cliente.
3. Realizar depósitos e saques.
4. Consultar o extrato com histórico das movimentações.
5. Transferir valores entre contas cadastradas.

## Diferenciais do projeto

- aderência ao diagrama UML proposto
- código organizado em camadas simples e fáceis de evoluir
- extras úteis sem descaracterizar a modelagem do desafio
- persistência local para enriquecer a demonstração
