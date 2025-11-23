"""
Analisador Léxico (Scanner) para a Linguagem Fantasy
Gera tokens para o analisador sintático/semântico

Palavras-chave: LOS, FOD, FAH, JUN, KEL, FUS, HON, print, assign, HIM, NUST, ANRK, AAN, KO
Operadores: +, -, :=, ;, ., (, )
Identificadores: [a-zA-Z_][a-zA-Z0-9_]*
Números: [0-9]+
"""

import re
from enum import Enum
from parser_integrated import Token

class TokenType(Enum):
    """Tipos de tokens da linguagem"""
    # Palavras-chave de controle
    LOS = "LOS"           # if
    FOD = "FOD"           # while (início)
    FAH = "FAH"           # while/for (separador)
    JUN = "JUN"           # return
    KEL = "KEL"           # module
    FUS = "FUS"           # declaração
    
    # I/O
    HON = "HON"           # input
    PRINT = "print"       # output
    
    # Operadores lógicos
    NUST = "NUST"         # not
    ANRK = "ANRK"         # and
    AAN = "AAN"           # or
    KO = "KO"             # in/pertence
    
    # Outros
    ASSIGN = "assign"     # palavra-chave assign
    HIM = "HIM"           # this/self
    
    # Identificadores e literais
    ID = "id"             # identificador
    NUM = "num"           # número
    
    # Operadores e pontuação
    PLUS = "+"            # adição
    MINUS = "-"           # subtração
    ASSIGN_OP = ":="      # atribuição
    SEMICOLON = ";"       # ponto-e-vírgula
    DOT = "."             # ponto
    LPAREN = "("          # parêntese esquerdo
    RPAREN = ")"          # parêntese direito
    
    # Especiais
    EOF = "$"             # fim de arquivo
    ERROR = "ERROR"       # erro léxico


class LexicalError(Exception):
    """Exceção para erros léxicos"""
    def __init__(self, message, line, column, char):
        self.message = message
        self.line = line
        self.column = column
        self.char = char
        super().__init__(f"ERRO LÉXICO (Linha {line}, Coluna {column}): {message}")


class Lexer:
    """Analisador Léxico"""
    
    # Palavras reservadas da linguagem
    KEYWORDS = {
        'LOS': TokenType.LOS,
        'FOD': TokenType.FOD,
        'FAH': TokenType.FAH,
        'JUN': TokenType.JUN,
        'KEL': TokenType.KEL,
        'FUS': TokenType.FUS,
        'HON': TokenType.HON,
        'print': TokenType.PRINT,
        'assign': TokenType.ASSIGN,
        'HIM': TokenType.HIM,
        'NUST': TokenType.NUST,
        'ANRK': TokenType.ANRK,
        'AAN': TokenType.AAN,
        'KO': TokenType.KO,
    }
    
    def __init__(self, source_code):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.errors = []
    
    def current_char(self):
        """Retorna o caractere atual"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset=1):
        """Olha caractere à frente sem avançar"""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self):
        """Avança para o próximo caractere"""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self):
        """Pula espaços em branco"""
        while self.current_char() and self.current_char() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        """Pula comentários de linha (#) e bloco (/* */)"""
        char = self.current_char()
        
        # Comentário de linha: # até o fim da linha
        if char == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
            self.advance()  # Pula o \n
            return True
        
        # Comentário de bloco: /* ... */
        if char == '/' and self.peek_char() == '*':
            self.advance()  # Pula /
            self.advance()  # Pula *
            
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()  # Pula *
                    self.advance()  # Pula /
                    return True
                self.advance()
            
            # Comentário não fechado
            self.errors.append(LexicalError(
                "Comentário de bloco não fechado",
                self.line, self.column, "/*"
            ))
            return True
        
        return False
    
    def read_number(self):
        """Lê um número inteiro"""
        start_line = self.line
        start_col = self.column
        num_str = ""
        
        while self.current_char() and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()
        
        value = int(num_str)
        return Token(TokenType.NUM.value, num_str, start_line, start_col, value)
    
    def read_identifier_or_keyword(self):
        """Lê identificador ou palavra-chave"""
        start_line = self.line
        start_col = self.column
        text = ""
        
        # Identificador: [a-zA-Z_][a-zA-Z0-9_]*
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            text += self.current_char()
            self.advance()
        
        # Verifica se é palavra reservada
        token_type = self.KEYWORDS.get(text, TokenType.ID)
        
        return Token(token_type.value, text, start_line, start_col, text)
    
    def read_operator(self):
        """Lê operadores"""
        start_line = self.line
        start_col = self.column
        char = self.current_char()
        
        # Operador de atribuição :=
        if char == ':' and self.peek_char() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.ASSIGN_OP.value, ":=", start_line, start_col, ":=")
        
        # Operadores simples
        operators = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            ';': TokenType.SEMICOLON,
            '.': TokenType.DOT,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
        }
        
        if char in operators:
            token_type = operators[char]
            self.advance()
            return Token(token_type.value, char, start_line, start_col, char)
        
        return None
    
    def tokenize(self):
        """Analisa o código fonte e gera lista de tokens"""
        self.tokens = []
        self.errors = []
        
        while self.position < len(self.source):
            # Pula espaços e comentários
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # Verifica comentários
            if self.skip_comment():
                continue
            
            char = self.current_char()
            start_line = self.line
            start_col = self.column
            
            # Números
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identificadores e palavras-chave
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier_or_keyword())
                continue
            
            # Operadores
            operator_token = self.read_operator()
            if operator_token:
                self.tokens.append(operator_token)
                continue
            
            # Caractere inválido
            error = LexicalError(
                f"Caractere inválido '{char}'",
                start_line, start_col, char
            )
            self.errors.append(error)
            self.advance()
        
        # Adiciona token EOF
        self.tokens.append(Token(TokenType.EOF.value, "$", self.line, self.column, "$"))
        
        return self.tokens
    
    def print_tokens(self):
        """Imprime lista de tokens formatada"""
        print("\n" + "="*80)
        print("FITA DE TOKENS")
        print("="*80)
        print(f"{'#':<5} {'Tipo':<15} {'Lexema':<20} {'Linha':<8} {'Coluna':<8} {'Valor'}")
        print("-"*80)
        
        for i, token in enumerate(self.tokens, 1):
            valor_str = str(token.value) if token.value else "-"
            if len(valor_str) > 20:
                valor_str = valor_str[:17] + "..."
            
            print(f"{i:<5} {token.type:<15} {token.lexeme:<20} {token.line:<8} {token.column:<8} {valor_str}")
        
        print("="*80)
        print(f"Total de tokens: {len(self.tokens)}\n")
    
    def has_errors(self):
        """Verifica se há erros léxicos"""
        return len(self.errors) > 0
    
    def print_errors(self):
        """Imprime erros léxicos"""
        if self.errors:
            print("\n" + "="*80)
            print("ERROS LÉXICOS")
            print("="*80)
            for error in self.errors:
                print(f"  ✗ {error}")
            print("="*80 + "\n")


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

def exemplo_declaracao():
    """Exemplo: Declaração de variável"""
    print("\n>>> EXEMPLO 1: Declaração de Variável")
    print("Código: FUS x := 10\n")
    
    code = "FUS x := 10"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    return tokens


def exemplo_io():
    """Exemplo: I/O"""
    print("\n>>> EXEMPLO 2: Input/Output")
    print("Código: HON input_var\n")
    
    code = "HON input_var"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    return tokens


def exemplo_expressao():
    """Exemplo: Expressão aritmética"""
    print("\n>>> EXEMPLO 3: Expressão Aritmética")
    print("Código: assign result := x + y - 10\n")
    
    code = "assign result := x + y - 10"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    return tokens


def exemplo_multiplas_linhas():
    """Exemplo: Programa com múltiplas linhas"""
    print("\n>>> EXEMPLO 4: Programa Completo")
    
    code = """# Programa exemplo
FUS x := 10
FUS y := 20
assign x := x + y
HON result"""
    
    print(f"Código:\n{code}\n")
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    return tokens


def exemplo_modulo():
    """Exemplo: Módulo KEL"""
    print("\n>>> EXEMPLO 5: Módulo KEL")
    
    code = """KEL player
FUS health := 100
JUN health"""
    
    print(f"Código:\n{code}\n")
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    return tokens


def exemplo_com_erro():
    """Exemplo: Código com erro léxico"""
    print("\n>>> EXEMPLO 6: Código com Erro Léxico")
    
    code = """FUS x := 10
assign y := @invalid
HON result"""
    
    print(f"Código:\n{code}\n")
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    if lexer.has_errors():
        lexer.print_errors()
    
    return tokens


def exemplo_integracao_com_parser():
    """Exemplo: Integração com parser sintático"""
    print("\n>>> EXEMPLO 7: Integração Léxico + Sintático + Semântico")
    
    from parser_integrated import SLRParserWithSemantics
    
    code = "FUS health := 100"
    print(f"Código: {code}\n")
    
    # Fase 1: Análise Léxica
    print("FASE 1: Análise Léxica")
    print("-" * 80)
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    lexer.print_tokens()
    
    if lexer.has_errors():
        lexer.print_errors()
        return False
    
    # Fase 2 e 3: Análise Sintática + Semântica
    print("\nFASE 2 & 3: Análise Sintática e Semântica")
    print("-" * 80)
    parser = SLRParserWithSemantics(verbose=True)
    sucesso = parser.parse(tokens)
    
    print()
    parser.print_report()
    
    return sucesso


def main():
    """Executa todos os exemplos"""
    print("\n" + "="*80)
    print("ANALISADOR LÉXICO - LINGUAGEM FANTASY")
    print("="*80)
    
    exemplo_declaracao()
    exemplo_io()
    exemplo_expressao()
    exemplo_multiplas_linhas()
    exemplo_modulo()
    exemplo_com_erro()
    
    print("\n" + "="*80)
    print("INTEGRAÇÃO COMPLETA: LÉXICO → SINTÁTICO → SEMÂNTICO")
    print("="*80)
    exemplo_integracao_com_parser()


if __name__ == "__main__":
    main()
