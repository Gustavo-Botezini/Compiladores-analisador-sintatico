"""
Parser SLR(1) Integrado com Análise Semântica
Inclui: Tratamento de erros, Tabela de Símbolos, Atributos e Valores
"""

from SLR import closures
from goto import transitions
from terminais import terminals
from nao_terminais import nonterminals
from follow import FOLLOW
from symbol_table import SymbolTable

class Token:
    """Token com atributos completos para análise semântica"""
    def __init__(self, token_type, lexeme, line, column=0, value=None):
        self.type = token_type      # Tipo do token (id, num, etc)
        self.lexeme = lexeme          # Texto literal (nome da variável, valor)
        self.line = line              # Linha no código fonte
        self.column = column          # Coluna no código fonte
        self.value = value            # Valor semântico (para num, strings)
    
    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', L{self.line})"


class SemanticError(Exception):
    """Exceção para erros semânticos"""
    def __init__(self, message, line, column=0, error_type="SEMANTIC"):
        self.message = message
        self.line = line
        self.column = column
        self.error_type = error_type
        super().__init__(f"{error_type} ERROR (Line {line}): {message}")


class SLRParserWithSemantics:
    """Parser SLR(1) com análise semântica integrada"""
    
    def __init__(self, verbose=True):
        self.stack = [0]
        self.symbols = []             # Pilha de símbolos sintáticos
        self.attributes = []          # Pilha de atributos semânticos
        self.closures = closures
        self.transitions = transitions
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.follow = FOLLOW
        self.productions = self._extract_productions()
        self.symbol_table = SymbolTable()
        self.verbose = verbose
        self.errors = []              # Lista de erros (sintáticos + semânticos)
        self.warnings = []
    
    def _extract_productions(self):
        """Extrai produções dos closures"""
        prods = {}
        for state, closure in self.closures.items():
            if isinstance(closure, set):
                for item in closure:
                    if len(item) == 2:
                        lhs, rhs = item
                        if len(rhs) > 0 and rhs[-1] == ".":
                            symbols = [s for s in rhs[:-1] if s != "."]
                            if not symbols:
                                symbols = ["epsilon"]
                            prods[state] = (lhs, symbols)
            elif isinstance(closure, list):
                for item in closure:
                    if "->" in item and item.endswith("."):
                        parts = item.split("->")
                        lhs = parts[0].strip()
                        rhs = parts[1].strip().rstrip(".")
                        if rhs == "epsilon":
                            symbols = ["epsilon"]
                        else:
                            symbols = rhs.split()
                        prods[state] = (lhs, symbols)
                        break
        return prods
    
    def semantic_action(self, production_lhs, production_rhs, attributes):
        """
        Executa ações semânticas durante redução
        
        Args:
            production_lhs: Lado esquerdo da produção
            production_rhs: Lado direito da produção (símbolos)
            attributes: Lista de atributos dos símbolos (na ordem da produção)
        
        Returns:
            Atributo sintetizado para o não-terminal da esquerda
        """
        
        # FUS id := EXPR - Declaração com atribuição
        if production_lhs == "CMD" and len(production_rhs) == 4:
            if production_rhs[0] == "FUS" and production_rhs[2] == ":=":
                var_token = attributes[1]  # Token do 'id'
                expr_value = attributes[3]  # Valor da expressão
                
                if self.verbose:
                    print(f"[Semântico] Declarando '{var_token.lexeme}' = {expr_value} (linha {var_token.line})")
                
                # Declara na tabela de símbolos
                self.symbol_table.declare(
                    var_token.lexeme,
                    symbol_type="variable",
                    line=var_token.line,
                    value=expr_value
                )
                
                return {"type": "declaration", "name": var_token.lexeme, "value": expr_value}
        
        # LHS := EXPR - Atribuição
        elif production_lhs == "CMD" and len(production_rhs) == 3:
            if production_rhs[1] == ":=":
                lhs_info = attributes[0]   # Informações do LHS
                expr_value = attributes[2] # Valor da expressão
                
                if lhs_info and "name" in lhs_info:
                    var_name = lhs_info["name"]
                    var_line = lhs_info.get("line", 0)
                    
                    if self.verbose:
                        print(f"[Semântico] Atribuindo '{var_name}' = {expr_value} (linha {var_line})")
                    
                    # Verifica se a variável foi declarada
                    symbol = self.symbol_table.lookup(var_name, line=var_line)
                    if symbol:
                        symbol.value = expr_value  # Atualiza o valor
                    
                    return {"type": "assignment", "name": var_name, "value": expr_value}
        
        # LHS -> assign id
        elif production_lhs == "LHS" and len(production_rhs) == 2:
            if production_rhs[0] == "assign":
                id_token = attributes[1]
                return {"name": id_token.lexeme, "line": id_token.line}
        
        # LHS -> HIM . id (acesso a membro)
        elif production_lhs == "LHS" and len(production_rhs) == 3:
            if production_rhs[0] == "HIM":
                id_token = attributes[2]
                return {"name": f"HIM.{id_token.lexeme}", "line": id_token.line, "scoped": True}
        
        # KEL id CMD - Módulo
        elif production_lhs == "CMD" and len(production_rhs) == 3:
            if production_rhs[0] == "KEL":
                module_token = attributes[1]
                
                if self.verbose:
                    print(f"[Semântico] Definindo módulo '{module_token.lexeme}' (linha {module_token.line})")
                
                # Nota: enter_scope/exit_scope devem ser chamados durante o parsing
                # Aqui apenas registramos o módulo
                self.symbol_table.declare(
                    module_token.lexeme,
                    symbol_type="module",
                    line=module_token.line
                )
                
                return {"type": "module", "name": module_token.lexeme}
        
        # IO id - Input/Output
        elif production_lhs == "CMD" and len(production_rhs) == 2:
            if production_rhs[0] == "IO":
                id_token = attributes[1]
                
                if self.verbose:
                    print(f"[Semântico] I/O com '{id_token.lexeme}' (linha {id_token.line})")
                
                # Verifica se foi declarado
                self.symbol_table.lookup(id_token.lexeme, line=id_token.line)
                
                return {"type": "io", "name": id_token.lexeme}
        
        # JUN EXPR - Return
        elif production_lhs == "CMD" and len(production_rhs) == 2:
            if production_rhs[0] == "JUN":
                expr_value = attributes[1]
                
                if self.verbose:
                    print(f"[Semântico] Return {expr_value}")
                
                return {"type": "return", "value": expr_value}
        
        # FACTOR -> id (uso de variável)
        elif production_lhs == "FACTOR" and len(production_rhs) == 1:
            if production_rhs[0] == "id":
                id_token = attributes[0]
                
                # Busca na tabela de símbolos
                symbol = self.symbol_table.lookup(id_token.lexeme, line=id_token.line)
                
                if symbol:
                    return symbol.value if symbol.value is not None else f"${id_token.lexeme}"
                else:
                    return f"${id_token.lexeme}"  # Placeholder
        
        # FACTOR -> num
        elif production_lhs == "FACTOR" and len(production_rhs) == 1:
            if production_rhs[0] == "num":
                num_token = attributes[0]
                return num_token.value if hasattr(num_token, 'value') else num_token.lexeme
        
        # EXPR -> TERM EXPR'
        elif production_lhs == "EXPR" and len(production_rhs) == 2:
            term_value = attributes[0]
            expr_prime = attributes[1]
            
            if expr_prime and isinstance(expr_prime, dict) and "op" in expr_prime:
                # Há operação: term op term'
                return f"({term_value} {expr_prime['op']} {expr_prime['right']})"
            else:
                return term_value
        
        # EXPR' -> OP TERM EXPR'
        elif production_lhs == "EXPR'" and len(production_rhs) == 3:
            op = attributes[0]
            term = attributes[1]
            expr_prime = attributes[2]
            
            if expr_prime and isinstance(expr_prime, dict) and "op" in expr_prime:
                return {"op": op, "right": f"({term} {expr_prime['op']} {expr_prime['right']})"}
            else:
                return {"op": op, "right": term}
        
        # EXPR' -> epsilon
        elif production_lhs == "EXPR'" and production_rhs == ["epsilon"]:
            return None
        
        # OP -> operadores
        elif production_lhs == "OP":
            return attributes[0] if attributes else production_rhs[0]
        
        # TERM -> FACTOR
        elif production_lhs == "TERM" and len(production_rhs) == 1:
            return attributes[0]
        
        # TERM -> UNARY
        elif production_lhs == "TERM" and production_rhs == ["UNARY"]:
            return attributes[0]
        
        # UNARY -> NUST TERM
        elif production_lhs == "UNARY" and len(production_rhs) == 2:
            term_value = attributes[1]
            return f"(NOT {term_value})"
        
        # Padrão: retorna primeiro atributo ou None
        return attributes[0] if attributes else None
    
    def parse(self, tokens):
        """
        Parsing com análise semântica integrada
        
        Args:
            tokens: Lista de objetos Token
        """
        if self.verbose:
            print("=== Analise Sintatica e Semantica SLR(1) ===\n")
        
        token_index = 0
        current_token = tokens[token_index] if token_index < len(tokens) else Token("$", "$", 0)
        step = 1
        
        try:
            while True:
                state = self.stack[-1]
                lookahead = current_token.type
                
                if self.verbose:
                    print(f"Passo {step}: Stack={self.stack}, Estado={state}, Token={current_token}")
                
                # Aceitação
                if state == 1 and lookahead == "$":
                    if self.verbose:
                        print("\n[OK] ANALISE SINTATICA ACEITA!\n")
                    
                    # Finaliza análise semântica
                    self.symbol_table.check_unused_symbols()
                    self.warnings.extend(self.symbol_table.warnings)
                    self.errors.extend(self.symbol_table.errors)
                    
                    return not self.has_errors()
                
                # SHIFT
                if (state, lookahead) in self.transitions:
                    next_state = self.transitions[(state, lookahead)]
                    if self.verbose:
                        print(f"  SHIFT -> {next_state}\n")
                    
                    self.stack.append(next_state)
                    self.symbols.append(lookahead)
                    self.attributes.append(current_token)  # Atributo é o token
                    
                    token_index += 1
                    current_token = tokens[token_index] if token_index < len(tokens) else Token("$", "$", 0)
                    step += 1
                    continue
                
                # Epsilon transition
                if (state, "epsilon") in self.transitions:
                    next_state = self.transitions[(state, "epsilon")]
                    if next_state == 38:
                        if (state, "EXPR'") in self.transitions:
                            expr_state = self.transitions[(state, "EXPR'")]
                            if self.verbose:
                                print(f"  REDUCE EXPR' -> epsilon, GOTO({state}, EXPR') = {expr_state}\n")
                            self.stack.append(expr_state)
                            self.symbols.append("EXPR'")
                            self.attributes.append(None)  # EXPR' -> epsilon não tem valor
                            step += 1
                            continue
                
                # GOTO para não-terminais com epsilon
                found_goto = False
                for nt in self.nonterminals:
                    if (state, nt) in self.transitions and nt == "EXPR'" and lookahead in self.follow.get("EXPR'", set()):
                        next_state = self.transitions[(state, nt)]
                        if self.verbose:
                            print(f"  REDUCE EXPR' -> epsilon, GOTO({state}, {nt}) = {next_state}\n")
                        self.stack.append(next_state)
                        self.symbols.append(nt)
                        self.attributes.append(None)
                        step += 1
                        found_goto = True
                        break
                
                if found_goto:
                    continue
                
                # REDUCE
                if state in self.productions:
                    lhs, rhs = self.productions[state]
                    
                    if lookahead in self.follow.get(lhs, set()) or lookahead == "$":
                        if self.verbose:
                            print(f"  REDUCE {lhs} -> {' '.join(rhs)}")
                        
                        # Coleta atributos dos símbolos da produção
                        prod_attributes = []
                        if rhs != ["epsilon"]:
                            prod_attributes = self.attributes[-len(rhs):] if len(rhs) > 0 else []
                        
                        # Ação semântica
                        try:
                            synthesized_attr = self.semantic_action(lhs, rhs, prod_attributes)
                        except Exception as e:
                            self.errors.append(f"Erro em ação semântica: {e}")
                            synthesized_attr = None
                        
                        # Remove símbolos da pilha
                        if rhs != ["epsilon"]:
                            for _ in range(len(rhs)):
                                if self.stack:
                                    self.stack.pop()
                                if self.symbols:
                                    self.symbols.pop()
                                if self.attributes:
                                    self.attributes.pop()
                        
                        state_after = self.stack[-1] if self.stack else 0
                        
                        # GOTO
                        if (state_after, lhs) in self.transitions:
                            goto_state = self.transitions[(state_after, lhs)]
                            if self.verbose:
                                print(f"  GOTO({state_after}, {lhs}) = {goto_state}\n")
                            
                            self.stack.append(goto_state)
                            self.symbols.append(lhs)
                            self.attributes.append(synthesized_attr)
                            
                            step += 1
                            continue
                        else:
                            error_msg = f"GOTO({state_after}, {lhs}) não encontrado"
                            self.errors.append(f"ERRO SINTATICO (Linha {current_token.line}): {error_msg}")
                            return False
                
                # Erro sintatico
                error_msg = f"Token inesperado '{current_token.lexeme}' (tipo: {lookahead})"
                self.errors.append(f"ERRO SINTATICO (Linha {current_token.line}): {error_msg}")
                return False
        
        except Exception as e:
            self.errors.append(f"ERRO FATAL: {str(e)}")
            return False
    
    def has_errors(self):
        """Verifica se há erros"""
        return len(self.errors) > 0 or self.symbol_table.has_errors()
    
    def print_report(self):
        """Imprime relatório completo de erros e avisos"""
        print("\n" + "="*70)
        print("RELATORIO DE ANALISE")
        print("="*70)
        
        if self.errors or self.symbol_table.errors:
            print("\n[X] ERROS ENCONTRADOS:")
            for error in self.errors:
                print(f"  - {error}")
            for error in self.symbol_table.errors:
                print(f"  - {error}")
        else:
            print("\n[OK] Nenhum erro encontrado")
        
        if self.warnings or self.symbol_table.warnings:
            print("\n[!] AVISOS:")
            for warning in self.warnings:
                print(f"  - {warning}")
            for warning in self.symbol_table.warnings:
                print(f"  - {warning}")
        
        print("\n" + "="*70)
        print("TABELA DE SIMBOLOS")
        print("="*70)
        self.symbol_table.print_table()
        print("="*70 + "\n")
    
    def reset(self):
        """Reinicia o parser"""
        self.stack = [0]
        self.symbols = []
        self.attributes = []
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

def exemplo_completo():
    """Exemplo completo com todos os recursos"""
    
    parser = SLRParserWithSemantics(verbose=True)
    
    # Programa simples: FUS x := 10
    tokens = [
        Token("FUS", "FUS", line=1),
        Token("id", "x", line=1, value="x"),
        Token(":=", ":=", line=1),
        Token("num", "10", line=1, value=10),
        Token("$", "$", line=1)
    ]
    
    print("="*70)
    print("PROGRAMA: FUS x := 10")
    print("="*70 + "\n")
    
    sucesso = parser.parse(tokens)
    parser.print_report()
    
    return sucesso


def exemplo_io():
    """Exemplo de I/O"""
    
    parser = SLRParserWithSemantics(verbose=True)
    
    # Primeiro declara, depois usa
    tokens = [
        Token("HON", "HON", line=1),
        Token("id", "input_var", line=1, value="input_var"),
        Token("$", "$", line=1)
    ]
    
    print("="*70)
    print("PROGRAMA: HON input_var")
    print("="*70 + "\n")
    
    sucesso = parser.parse(tokens)
    parser.print_report()
    
    return sucesso


def exemplo_atribuicao():
    """Exemplo de atribuição com valor"""
    
    parser = SLRParserWithSemantics(verbose=True)
    
    # Declara e depois atribui novo valor
    tokens = [
        Token("assign", "assign", line=1),
        Token("id", "x", line=1, value="x"),
        Token(":=", ":=", line=1),
        Token("num", "42", line=1, value=42),
        Token("$", "$", line=1)
    ]
    
    print("="*70)
    print("PROGRAMA: assign x := 42")
    print("="*70 + "\n")
    
    sucesso = parser.parse(tokens)
    parser.print_report()
    
    return sucesso


def exemplo_com_erros():
    """Exemplo com erros semânticos"""
    
    parser = SLRParserWithSemantics(verbose=False)
    
    # Programa com erros: assign z := 10 (z não declarado)
    tokens = [
        Token("assign", "assign", line=1),
        Token("id", "z", line=1, value="z"),
        Token(":=", ":=", line=1),
        Token("num", "10", line=1, value=10),
        Token("$", "$", line=1)
    ]
    
    print("="*70)
    print("PROGRAMA COM ERRO: assign z := 10 (z não declarado)")
    print("="*70 + "\n")
    
    sucesso = parser.parse(tokens)
    parser.print_report()
    
    return sucesso


def main():
    print("\n>>> EXEMPLO 1: Declaração FUS\n")
    exemplo_completo()
    
    print("\n\n>>> EXEMPLO 2: I/O (HON)\n")
    exemplo_io()
    
    print("\n\n>>> EXEMPLO 3: Atribuição\n")
    exemplo_atribuicao()
    
    print("\n\n>>> EXEMPLO 4: Erro Semântico\n")
    exemplo_com_erros()


if __name__ == "__main__":
    main()

