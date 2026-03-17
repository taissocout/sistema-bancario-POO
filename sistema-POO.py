"""
Sistema Bancário - DIO Trilha Python
Implementação com POO seguindo modelo UML
"""

from abc import ABC, abstractmethod
from datetime import datetime


# ─────────────────────────────────────────────
#  ITERADOR DE CONTAS
# ─────────────────────────────────────────────
class ContasIterador:
    def __init__(self, contas):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._contas):
            raise StopIteration
        conta = self._contas[self._index]
        self._index += 1
        return conta


# ─────────────────────────────────────────────
#  HISTÓRICO
# ─────────────────────────────────────────────
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for t in self._transacoes:
            if tipo_transacao is None or t["tipo"].lower() == tipo_transacao.lower():
                yield t


# ─────────────────────────────────────────────
#  TRANSAÇÕES (ABC)
# ─────────────────────────────────────────────
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        ...

    @abstractmethod
    def registrar(self, conta):
        ...


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self._valor):
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self._valor):
            conta.historico.adicionar_transacao(self)


# ─────────────────────────────────────────────
#  CONTA (BASE)
# ─────────────────────────────────────────────
class Conta:
    _numero_sequencial = 1

    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n❌ Operação inválida: valor deve ser positivo.")
            return False
        if valor > self._saldo:
            print("\n❌ Saldo insuficiente.")
            return False
        self._saldo -= valor
        print(f"\n✅ Saque de R$ {valor:.2f} realizado com sucesso!")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n❌ Operação inválida: valor deve ser positivo.")
            return False
        self._saldo += valor
        print(f"\n✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True


# ─────────────────────────────────────────────
#  CONTA CORRENTE
# ─────────────────────────────────────────────
class ContaCorrente(Conta):
    LIMITE_PADRAO = 500.0
    LIMITE_SAQUES_PADRAO = 3

    def __init__(self, numero, cliente, limite=LIMITE_PADRAO, limite_saques=LIMITE_SAQUES_PADRAO):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero, limite=LIMITE_PADRAO, limite_saques=LIMITE_SAQUES_PADRAO):
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor):
        saques_realizados = sum(
            1 for t in self.historico.transacoes if t["tipo"] == "Saque"
        )

        if saques_realizados >= self._limite_saques:
            print(f"\n❌ Limite de {self._limite_saques} saques diários atingido.")
            return False

        if valor > self._limite:
            print(f"\n❌ Valor excede o limite por saque (R$ {self._limite:.2f}).")
            return False

        return super().sacar(valor)

    def __repr__(self):
        return (
            f"ContaCorrente("
            f"ag={self._agencia}, "
            f"nº={self._numero}, "
            f"titular={self._cliente.nome})"
        )

    def __str__(self):
        return (
            f"\n{'─'*40}"
            f"\nAgência:\t{self._agencia}"
            f"\nC/C:\t\t{self._numero}"
            f"\nTitular:\t{self._cliente.nome}"
            f"\nSaldo:\t\tR$ {self._saldo:.2f}"
            f"\n{'─'*40}"
        )


# ─────────────────────────────────────────────
#  CLIENTE / PESSOA FÍSICA
# ─────────────────────────────────────────────
class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []

    @property
    def contas(self):
        return self._contas

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

    @property
    def cpf(self):
        return self._cpf

    @property
    def nome(self):
        return self._nome

    def __repr__(self):
        return f"PessoaFisica(cpf={self._cpf}, nome={self._nome})"

    def __str__(self):
        return (
            f"\n{'─'*40}"
            f"\nNome:\t\t{self._nome}"
            f"\nCPF:\t\t{self._cpf}"
            f"\nNascimento:\t{self._data_nascimento}"
            f"\nEndereço:\t{self._endereco}"
            f"\n{'─'*40}"
        )


# ─────────────────────────────────────────────
#  BANCO (GERENCIADOR)
# ─────────────────────────────────────────────
class Banco:
    def __init__(self):
        self._clientes = []
        self._contas = []
        self._proximo_numero_conta = 1

    @property
    def clientes(self):
        return self._clientes

    @property
    def contas(self):
        return self._contas

    def buscar_cliente(self, cpf):
        return next((c for c in self._clientes if c.cpf == cpf), None)

    def buscar_conta_cliente(self, cliente):
        if not cliente.contas:
            print("\n❌ Cliente não possui contas cadastradas.")
            return None
        if len(cliente.contas) == 1:
            return cliente.contas[0]
        # Múltiplas contas → escolher
        print("\nContas disponíveis:")
        for i, conta in enumerate(cliente.contas, 1):
            print(f"  [{i}] Ag {conta.agencia} | C/C {conta.numero}")
        try:
            idx = int(input("Escolha a conta: ")) - 1
            return cliente.contas[idx]
        except (ValueError, IndexError):
            print("\n❌ Opção inválida.")
            return None

    def cadastrar_cliente(self):
        cpf = input("CPF (somente números): ").strip()
        if self.buscar_cliente(cpf):
            print("\n❌ Já existe um cliente com esse CPF.")
            return
        nome = input("Nome completo: ").strip()
        data_nasc = input("Data de nascimento (dd/mm/aaaa): ").strip()
        logradouro = input("Logradouro: ").strip()
        numero = input("Número: ").strip()
        bairro = input("Bairro: ").strip()
        cidade = input("Cidade: ").strip()
        uf = input("UF: ").strip()
        endereco = f"{logradouro}, {numero} - {bairro} - {cidade}/{uf}"
        cliente = PessoaFisica(cpf, nome, data_nasc, endereco)
        self._clientes.append(cliente)
        print(f"\n✅ Cliente {nome} cadastrado com sucesso!")

    def criar_conta(self):
        cpf = input("CPF do titular: ").strip()
        cliente = self.buscar_cliente(cpf)
        if not cliente:
            print("\n❌ Cliente não encontrado.")
            return
        numero = self._proximo_numero_conta
        self._proximo_numero_conta += 1
        conta = ContaCorrente.nova_conta(cliente, numero)
        cliente.adicionar_conta(conta)
        self._contas.append(conta)
        print(f"\n✅ Conta corrente nº {numero} criada para {cliente.nome}!")

    def depositar(self):
        cpf = input("CPF do titular: ").strip()
        cliente = self.buscar_cliente(cpf)
        if not cliente:
            print("\n❌ Cliente não encontrado.")
            return
        conta = self.buscar_conta_cliente(cliente)
        if not conta:
            return
        try:
            valor = float(input("Valor do depósito: R$ "))
        except ValueError:
            print("\n❌ Valor inválido.")
            return
        cliente.realizar_transacao(conta, Deposito(valor))

    def sacar(self):
        cpf = input("CPF do titular: ").strip()
        cliente = self.buscar_cliente(cpf)
        if not cliente:
            print("\n❌ Cliente não encontrado.")
            return
        conta = self.buscar_conta_cliente(cliente)
        if not conta:
            return
        try:
            valor = float(input("Valor do saque: R$ "))
        except ValueError:
            print("\n❌ Valor inválido.")
            return
        cliente.realizar_transacao(conta, Saque(valor))

    def exibir_extrato(self):
        cpf = input("CPF do titular: ").strip()
        cliente = self.buscar_cliente(cpf)
        if not cliente:
            print("\n❌ Cliente não encontrado.")
            return
        conta = self.buscar_conta_cliente(cliente)
        if not conta:
            return

        print(f"\n{'═'*40}")
        print(f"{'EXTRATO BANCÁRIO':^40}")
        print(f"{'═'*40}")
        transacoes = list(conta.historico.gerar_relatorio())
        if not transacoes:
            print("Nenhuma movimentação registrada.")
        else:
            for t in transacoes:
                sinal = "+" if t["tipo"] == "Deposito" else "-"
                print(f"  {t['data']}  {t['tipo']:<10}  {sinal}R$ {t['valor']:.2f}")
        print(f"{'─'*40}")
        print(f"  Saldo atual: R$ {conta.saldo:.2f}")
        print(f"{'═'*40}")

    def listar_contas(self):
        print(f"\n{'═'*40}")
        print(f"{'CONTAS CADASTRADAS':^40}")
        print(f"{'═'*40}")
        for conta in ContasIterador(self._contas):
            print(conta)

    def listar_clientes(self):
        print(f"\n{'═'*40}")
        print(f"{'CLIENTES CADASTRADOS':^40}")
        print(f"{'═'*40}")
        if not self._clientes:
            print("Nenhum cliente cadastrado.")
        for cliente in self._clientes:
            print(cliente)


# ─────────────────────────────────────────────
#  MENU PRINCIPAL
# ─────────────────────────────────────────────
MENU = """
╔══════════════════════════════════╗
║       BANCO DIO  •  Sistema      ║
╠══════════════════════════════════╣
║  [d] Depositar                   ║
║  [s] Sacar                       ║
║  [e] Extrato                     ║
║  [nc] Nova conta                 ║
║  [lc] Listar contas              ║
║  [nu] Novo usuário               ║
║  [lu] Listar usuários            ║
║  [q] Sair                        ║
╚══════════════════════════════════╝
=> """


def main():
    banco = Banco()

    while True:
        opcao = input(MENU).strip().lower()

        if opcao == "d":
            banco.depositar()
        elif opcao == "s":
            banco.sacar()
        elif opcao == "e":
            banco.exibir_extrato()
        elif opcao == "nc":
            banco.criar_conta()
        elif opcao == "lc":
            banco.listar_contas()
        elif opcao == "nu":
            banco.cadastrar_cliente()
        elif opcao == "lu":
            banco.listar_clientes()
        elif opcao == "q":
            print("\n👋 Até logo!\n")
            break
        else:
            print("\n⚠️  Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
