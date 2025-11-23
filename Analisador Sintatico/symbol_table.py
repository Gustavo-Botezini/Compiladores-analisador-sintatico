"""
Tabela de Símbolos para o Analisador Semântico
Gerencia identificadores, escopos e declarações da linguagem fantasy
"""

class Symbol:
    """Representa um símbolo (identificador) na tabela"""
    def __init__(self, name, symbol_type, scope, line=None, value=None):
        self.name = name              # Nome do identificador
        self.symbol_type = symbol_type # Tipo: 'variable', 'module', 'parameter'
        self.scope = scope            # Escopo onde foi declarado
        self.line = line              # Linha de declaração (para mensagens de erro)
        self.value = value            # Valor inicial (opcional)
        self.used = False             # Marca se foi usado (para avisos)
    
    def __repr__(self):
        return f"Symbol({self.name}, type={self.symbol_type}, scope={self.scope})"


class Scope:
    """Representa um escopo (bloco de código)"""
    def __init__(self, name, parent=None):
        self.name = name              # Nome do escopo (ex: 'global', 'KEL_player')
        self.parent = parent          # Escopo pai (para aninhamento)
        self.symbols = {}             # Dicionário de símbolos neste escopo
        self.children = []            # Escopos filhos
    
    def define(self, symbol):
        """Define um novo símbolo neste escopo"""
        if symbol.name in self.symbols:
            return False  # Já existe
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name, recursive=True):
        """Procura um símbolo neste escopo (e nos pais se recursive=True)"""
        if name in self.symbols:
            return self.symbols[name]
        
        if recursive and self.parent:
            return self.parent.lookup(name, recursive=True)
        
        return None
    
    def __repr__(self):
        return f"Scope({self.name}, {len(self.symbols)} symbols)"


class SymbolTable:
    """Tabela de Símbolos com suporte a escopos aninhados"""
    
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.errors = []              # Lista de erros semânticos
        self.warnings = []            # Lista de avisos
    
    def enter_scope(self, scope_name):
        """Entra em um novo escopo (ex: ao entrar em KEL módulo)"""
        new_scope = Scope(scope_name, parent=self.current_scope)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        """Sai do escopo atual, voltando ao pai"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
        else:
            self.warnings.append("Tentativa de sair do escopo global")
    
    def declare(self, name, symbol_type='variable', line=None, value=None):
        """Declara um novo símbolo no escopo atual"""
        symbol = Symbol(name, symbol_type, self.current_scope.name, line, value)
        
        if not self.current_scope.define(symbol):
            self.errors.append(
                f"Erro semântico (linha {line}): '{name}' já foi declarado em '{self.current_scope.name}'"
            )
            return False
        
        return True
    
    def lookup(self, name, line=None, mark_used=True):
        """Busca um símbolo na tabela (escopo atual e pais)"""
        symbol = self.current_scope.lookup(name)
        
        if symbol is None:
            self.errors.append(
                f"Erro semântico (linha {line}): '{name}' não foi declarado"
            )
            return None
        
        if mark_used:
            symbol.used = True
        
        return symbol
    
    def lookup_in_scope(self, name, scope_name):
        """Busca um símbolo em um escopo específico (para HIM . id)"""
        # Busca o escopo pelo nome
        scope = self._find_scope(scope_name, self.global_scope)
        if scope:
            return scope.lookup(name, recursive=False)
        return None
    
    def _find_scope(self, scope_name, current):
        """Busca recursivamente um escopo pelo nome"""
        if current.name == scope_name:
            return current
        
        for child in current.children:
            result = self._find_scope(scope_name, child)
            if result:
                return result
        
        return None
    
    def check_unused_symbols(self):
        """Verifica símbolos declarados mas não usados"""
        self._check_unused_in_scope(self.global_scope)
    
    def _check_unused_in_scope(self, scope):
        """Verifica recursivamente símbolos não usados"""
        for name, symbol in scope.symbols.items():
            if not symbol.used and symbol.symbol_type == 'variable':
                self.warnings.append(
                    f"Aviso (linha {symbol.line}): variável '{name}' declarada mas não usada"
                )
        
        for child in scope.children:
            self._check_unused_in_scope(child)
    
    def print_table(self, scope=None, indent=0):
        """Imprime a tabela de símbolos formatada"""
        if scope is None:
            scope = self.global_scope
        
        print("  " * indent + f"Escopo: {scope.name}")
        for name, symbol in scope.symbols.items():
            used_mark = "✓" if symbol.used else " "
            print("  " * indent + f"  [{used_mark}] {name}: {symbol.symbol_type}")
        
        for child in scope.children:
            self.print_table(child, indent + 1)
    
    def has_errors(self):
        """Retorna True se houver erros semânticos"""
        return len(self.errors) > 0
    
    def print_errors(self):
        """Imprime todos os erros e avisos"""
        if self.errors:
            print("\n=== ERROS SEMÂNTICOS ===")
            for error in self.errors:
                print(f"  ✗ {error}")
        
        if self.warnings:
            print("\n=== AVISOS ===")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✓ Nenhum erro semântico encontrado")


# Exemplo de uso
if __name__ == "__main__":
    print("=== Teste da Tabela de Símbolos ===\n")
    
    st = SymbolTable()
    
    # Simula: FUS x := 10 (declaração global)
    print("1. Declarando 'x' no escopo global")
    st.declare("x", "variable", line=1, value=10)
    
    # Simula: assign y (uso sem declaração - ERRO)
    print("2. Usando 'y' sem declarar (erro esperado)")
    st.lookup("y", line=2)
    
    # Simula: KEL player { ... } (entra em módulo)
    print("3. Entrando no módulo 'player'")
    st.enter_scope("KEL_player")
    
    # Simula: FUS health := 100 (declaração no módulo)
    print("4. Declarando 'health' no módulo 'player'")
    st.declare("health", "variable", line=4, value=100)
    
    # Simula: assign x (referencia variável global)
    print("5. Usando 'x' global dentro do módulo")
    st.lookup("x", line=5)
    
    # Simula: FUS health := 50 (redeclaração - ERRO)
    print("6. Tentando redeclarar 'health' (erro esperado)")
    st.declare("health", "variable", line=6, value=50)
    
    # Simula: FUS mana := 20 (declaração não usada)
    print("7. Declarando 'mana' mas não usando")
    st.declare("mana", "variable", line=7, value=20)
    
    print("\n8. Saindo do módulo 'player'")
    st.exit_scope()
    
    # Verifica símbolos não usados
    print("\n9. Verificando símbolos não usados")
    st.check_unused_symbols()
    
    # Imprime a tabela completa
    print("\n=== Tabela de Símbolos ===")
    st.print_table()
    
    # Imprime erros e avisos
    st.print_errors()
