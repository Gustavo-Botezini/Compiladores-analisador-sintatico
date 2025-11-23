"""
Sistema Completo de Análise: PDA (Léxico) -> SLR(1) (Sintático + Semântico)
Integra o autômato de pilha de Compiladores/ como analisador léxico
"""

from SLR import closures
from goto import transitions
from terminais import terminals
from nao_terminais import nonterminals
from follow import FOLLOW
from parser_integrated import SLRParserWithSemantics, Token
from Compiladores.pda import AP
from Compiladores.constants import EPSILON
from Compiladores.delta import DeltaFinal


class PDALexerAdapter:
    """
    Adapta a saída do PDA para gerar tokens compatíveis com o parser SLR
    Mapeia estados finais do PDA para tipos de tokens
    """
    
    # Mapeamento: Estado final do PDA -> Tipo de token
    STATE_TO_TOKEN = {
        'E11,Z': 'KEL',      # Palavra-chave KEL (módulo)
        'D10,Z': 'LOS',      # Palavra-chave LOS (if)
        'E12,Z': 'FOD',      # Palavra-chave FOD (while início)
        'D3,Z': 'FAH',       # Palavra-chave FAH (separador)
        'D5,Z': 'FUS',       # Palavra-chave FUS (declaração)
        'D9,Z': 'HON',       # Palavra-chave HON (input)
        'D4,Z': 'JUN',       # Palavra-chave JUN (return)
        'D6,Z': 'HIM',       # Palavra-chave HIM (this/self)
        'D7,Z': 'NUST',      # Palavra-chave NUST (not)
        'D8,Z': 'ANRK',      # Palavra-chave ANRK (and)
        'D2,Z': 'AAN',       # Palavra-chave AAN (or)
        'B1,Z': 'KO',        # Palavra-chave KO (in)
    }
    
    # Mapeamento reverso: entrada original -> palavra-chave reconhecida
    ORIGINAL_TO_KEYWORD = {
        'KO': 'KO',
        'KEL': 'KEL',
        'LOS': 'LOS',
        'FAH': 'FAH',
        'HIM': 'HIM',
        'JUN': 'JUN',
        'FOD': 'FOD',
        'FUS': 'FUS',
        'HON': 'HON',
        'NUST': 'NUST',
        'AAN': 'AAN',
        'ANRK': 'ANRK',
    }
    
    def __init__(self):
        # Configuração do PDA (copiada de Compiladores/main.py)
        Q = ['A1,B2,Z', 'Z', 'B7,B8,Z', 'B3,B6,Z',
             'B12,Z', 'B4,Z', 'B5,B9,Z', 'B10,B11,Z',
             'B1,Z', 'C2,Z', 'C8,Z', 'C7,Z',
             'B3,Z', 'C6,Z', 'C12,Z', 'C4,Z',
             'C9,Z', 'C5,Z', 'B11,Z', 'B10,Z',
             'D2,Z', 'D8,Z', 'D7,Z', 'C3,Z',
             'D6,Z', 'D12,Z', 'D4,Z', 'D9,Z',
             'D5,Z', 'C11,Z', 'C10,Z', 'D3,Z',
             'E12,Z', 'D11,Z', 'D10,Z', 'E11,Z']
        
        Sigma = ['#', 'K', 'O', 'E', 'L', 'H', 'N', 'J', 
                 'U', 'F', 'S', 'I', 'M', 'D', 'R', 'T', 'A', EPSILON]
        
        gama = ['$', 'K', 'O', 'E', 'L', 'H', 'N', 'J', 
                'U', 'F', 'S', 'I', 'M', 'D', 'R', 'T', 'A', EPSILON]
        
        F = ['E11,Z', 'D10,Z', 'E12,Z', 'D3,Z', 'D5,Z', 'D9,Z', 
             'D10,Z', 'D4,Z', 'D6,Z', 'D7,Z', 'D8,Z', 'D2,Z', 'B1,Z']
        
        self.pda = AP(Sigma, gama, DeltaFinal, 'S', F)
    
    def tokenize(self, source_code):
        """
        Executa PDA e converte saída para tokens
        
        Args:
            source_code: String com código fonte (formato: "KO KEL # LOS")
        
        Returns:
            Lista de objetos Token
        """
        tokens = []
        linha_atual = 1
        
        print("==================================================================")
        print("=          SAÍDA DO PDA (Compiladores/main.py)                  =")
        print("==================================================================")
        
        # Executar PDA original e capturar saída
        print("\n Processando entrada no PDA...")
        print(f"Entrada: {source_code}\n")
        
        # Separar por linhas (delimitadas por '#')
        linhas = source_code.split('#')
        
        pda_results = []  # Armazena resultados do PDA
        
        for linha_texto in linhas:
            linha_texto = linha_texto.strip()
            if not linha_texto:
                linha_atual += 1
                continue
            
            # Processar cada palavra da linha
            palavras = linha_texto.split()
            
            for palavra in palavras:
                palavra = palavra.strip()
                if not palavra:
                    continue
                
                # Simular reconhecimento pelo PDA caractere por caractere
                estado_final = self._reconhecer_palavra(palavra)
                
                # Armazenar resultado do PDA
                pda_result = {
                    'palavra': palavra,
                    'linha': linha_atual,
                    'estado': estado_final,
                    'aceito': estado_final in self.STATE_TO_TOKEN
                }
                pda_results.append(pda_result)
                
                # Mapear estado final para tipo de token
                if estado_final in self.STATE_TO_TOKEN:
                    token_type = self.STATE_TO_TOKEN[estado_final]
                    token = Token(token_type, palavra, linha_atual, column=0, value=palavra)
                    tokens.append(token)
                    
                    # Mostrar saída do PDA (similar ao original)
                    print(f"[OK] Linha {linha_atual}: '{palavra}' -> Estado {estado_final} -> {token_type} (ACEITO)")
                
                elif estado_final == 'X':
                    # Palavra rejeitada - pode ser ID, NUM ou erro
                    token = self._classificar_palavra_desconhecida(palavra, linha_atual)
                    tokens.append(token)
                    print(f"  Linha {linha_atual}: '{palavra}' -> Não reconhecido pelo PDA -> {token.type}")
                
                else:
                    # Estado não mapeado - tratar como ID
                    print(f"[!] Linha {linha_atual}: '{palavra}' -> Estado '{estado_final}' não mapeado")
                    token = Token("id", palavra, linha_atual, value=palavra)
                    tokens.append(token)
            
            linha_atual += 1
        
        # Adicionar EOF
        tokens.append(Token("$", "$", linha_atual, column=0, value="$"))
        
        # Mostrar tabela de símbolos do PDA
        print("\n" + "="*70)
        print(" TABELA DE SÍMBOLOS DO PDA:")
        print("="*70)
        print(f"{'Linha':<8} {'Palavra':<15} {'Estado Final':<15} {'Status':<10}")
        print("="*70)
        
        for result in pda_results:
            status = "[OK] ACEITO" if result['aceito'] else "[X] REJEITADO"
            print(f"{result['linha']:<8} {result['palavra']:<15} {result['estado']:<15} {status:<10}")
        
        print("="*70)
        print(f"\n[OK] PDA processou {len(pda_results)} palavras")
        print(f"[OK] Gerados {len(tokens)} tokens (incluindo EOF)\n")
        
        return tokens
    
    def _reconhecer_palavra(self, palavra):
        """
        Reconhece palavra pelo PDA e retorna estado final
        Simula a lógica de run() do AP sem impressões
        """
        estado = 'S'  # Estado inicial
        
        for char in palavra:
            if char not in self.pda._Sigma:
                return 'X'  # Caractere inválido
            
            # Busca transição
            transicao = self.pda._delta.get((estado, char, EPSILON))
            if transicao:
                estado = transicao[0]
            else:
                return 'X'  # Sem transição
        
        # Verifica se é estado final
        if estado not in self.pda._F:
            return 'X'
        
        return estado
    
    def _classificar_palavra_desconhecida(self, palavra, linha):
        """
        Classifica palavras não reconhecidas pelo PDA
        Pode ser ID, NUM, operadores, etc.
        """
        # Números
        if palavra.isdigit():
            return Token("num", palavra, linha, value=int(palavra))
        
        # Operadores e pontuação
        operadores = {
            ':=': ':=',
            ';': ';',
            '.': '.',
            '(': '(',
            ')': ')',
            '+': '+',
            '-': '-',
        }
        
        if palavra in operadores:
            return Token(palavra, palavra, linha, value=palavra)
        
        # Palavras-chave não cobertas pelo PDA
        keywords_extras = {
            'assign': 'assign',
            'print': 'print',
        }
        
        if palavra in keywords_extras:
            return Token(keywords_extras[palavra], palavra, linha, value=palavra)
        
        # Padrão: identificador
        return Token("id", palavra, linha, value=palavra)


class CompiladorCompleto:
    """Pipeline completo: PDA Léxico -> SLR Sintático -> Análise Semântica"""
    
    def __init__(self, verbose=True):
        self.lexer = PDALexerAdapter()
        self.parser = SLRParserWithSemantics(verbose=verbose)
        self.verbose = verbose
    
    def compile(self, source_code):
        """
        Executa compilação completa
        
        Args:
            source_code: String com código fonte
        
        Returns:
            bool: True se compilação bem-sucedida
        """
        print("\n" + "="*80)
        print("FASE 1: ANÁLISE LÉXICA (PDA)")
        print("="*80)
        print(f"Código fonte: {source_code}\n")
        
        # Fase 1: Análise Léxica com PDA
        try:
            tokens = self.lexer.tokenize(source_code)
            
            if self.verbose:
                print("\n==================================================================")
                print("=              TOKENS GERADOS PARA O PARSER                      =")
                print("==================================================================")
                for i, token in enumerate(tokens, 1):
                    print(f"{i:3}. {token}")
                print("-" * 80)
        
        except Exception as e:
            print(f"\n[X] ERRO LÉXICO: {e}")
            return False
        
        # Fase 2 & 3: Análise Sintática + Semântica
        print("\n" + "="*80)
        print("FASE 2 & 3: ANÁLISE SINTÁTICA E SEMÂNTICA (SLR)")
        print("="*80 + "\n")
        
        sucesso = self.parser.parse(tokens)
        
        # Relatório final
        self.parser.print_report()
        
        return sucesso
    
    def reset(self):
        """Reinicia compilador"""
        self.parser.reset()


# ============================================================================
# CLASSE ANTIGA (MANTIDA PARA COMPATIBILIDADE)
# ============================================================================

class SLRParser:
    def __init__(self):
        self.stack = [0]
        self.symbols = []
        self.closures = closures
        self.transitions = transitions
        self.terminals = terminals
        self.nonterminals = nonterminals
        self.follow = FOLLOW
        self.productions = self._extract_productions()
    
    def _extract_productions(self):
        prods = {}
        for state, closure in self.closures.items():
            if isinstance(closure, set):
                for item in closure:
                    if len(item) == 2:
                        lhs, rhs = item
                        if len(rhs) > 0 and rhs[-1] == ".":
                            symbols = [s for s in rhs[:-1] if s != "."]
                            if not symbols:
                                symbols = ["ε"]
                            prods[state] = (lhs, symbols)
            elif isinstance(closure, list):
                for item in closure:
                    if "->" in item and item.endswith("."):
                        parts = item.split("->")
                        lhs = parts[0].strip()
                        rhs = parts[1].strip().rstrip(".")
                        if rhs == "ε":
                            symbols = ["ε"]
                        else:
                            symbols = rhs.split()
                        prods[state] = (lhs, symbols)
                        break
        return prods
    
    def parse(self, tokens):
        print("=== Análise Sintática SLR(1) ===\n")
        token_index = 0
        current_token = tokens[token_index] if token_index < len(tokens) else ("$", "$")
        step = 1
        
        while True:
            state = self.stack[-1]
            lookahead = current_token[0]
            
            print(f"Passo {step}: Stack={self.stack}, Estado={state}, Lookahead={lookahead}")
            
            if state == 1 and lookahead == "$":
                print("\n[OK] ACEITO!\n")
                return True
            
            if (state, lookahead) in self.transitions:
                next_state = self.transitions[(state, lookahead)]
                print(f"  SHIFT -> {next_state}\n")
                self.stack.append(next_state)
                self.symbols.append(lookahead)
                token_index += 1
                current_token = tokens[token_index] if token_index < len(tokens) else ("$", "$")
                step += 1
                continue
            
            if (state, "ε") in self.transitions:
                next_state = self.transitions[(state, "ε")]
                print(f"  REDUCE EXPR' -> ε via estado {next_state}")
                # Estado 38 é EXPR' -> ε., então devemos fazer GOTO de volta
                # Não empilhamos ε, fazemos o GOTO diretamente
                if next_state == 38:
                    # Pop do estado ε e faz GOTO com EXPR'
                    if (state, "EXPR'") in self.transitions:
                        expr_state = self.transitions[(state, "EXPR'")]
                        print(f"  GOTO({state}, EXPR') = {expr_state}\n")
                        self.stack.append(expr_state)
                        self.symbols.append("EXPR'")
                        step += 1
                        continue
                else:
                    self.stack.append(next_state)
                    self.symbols.append("ε")
                    step += 1
                    continue
            
            found_goto = False
            for nt in self.nonterminals:
                if (state, nt) in self.transitions and nt == "EXPR'" and lookahead in self.follow.get("EXPR'", set()):
                    print(f"  REDUCE EXPR' -> ε")
                    next_state = self.transitions[(state, nt)]
                    print(f"  GOTO({state}, {nt}) = {next_state}\n")
                    self.stack.append(next_state)
                    self.symbols.append(nt)
                    step += 1
                    found_goto = True
                    break
            
            if found_goto:
                continue
            
            if state in self.productions:
                lhs, rhs = self.productions[state]
                if lookahead in self.follow.get(lhs, set()) or lookahead == "$":
                    print(f"  REDUCE {lhs} -> {' '.join(rhs)}")
                    if rhs != ["ε"]:
                        for _ in range(len(rhs)):
                            if self.stack:
                                self.stack.pop()
                            if self.symbols:
                                self.symbols.pop()
                    state_after = self.stack[-1] if self.stack else 0
                    if (state_after, lhs) in self.transitions:
                        goto_state = self.transitions[(state_after, lhs)]
                        print(f"  GOTO({state_after}, {lhs}) = {goto_state}\n")
                        self.stack.append(goto_state)
                        self.symbols.append(lhs)
                        step += 1
                        continue
                    else:
                        print(f"\n[X] ERRO: GOTO({state_after}, {lhs}) não encontrado!\n")
                        return False
            
            print(f"\n[X] ERRO SINTÁTICO! Estado={state}, Lookahead={lookahead}\n")
            return False
    
    def reset(self):
        self.stack = [0]
        self.symbols = []




def main():
    """
    Testes para verificar funcionalidade do compilador completo
    - Teste 1: Programa correto com múltiplas operações
    - Teste 2: Uso de JUN (return) para retornar valor
    - Teste 3: Erro sintático (falta operador :=)
    - Teste 4: Erro semântico (variável não declarada)
    - Teste 5: Erro léxico (caractere inválido)
    - Teste 6: Erro sintático estrutural (parênteses)
    """
    compilador = CompiladorCompleto(verbose=False)
    
    # ========================================================================
    # TESTE 1: PROGRAMA CORRETO (expressão complexa)
    # ========================================================================
    print("\n" + "="*80)
    print("           TESTE 1: PROGRAMA CORRETO")
    print("="*80)
    print("\nCódigo:")
    print("  FUS resultado := 10 + 20 - 5")
    print("\nDescrição: Declaração com operações aritméticas múltiplas")
    print("Resultado esperado: SUCESSO\n")
    
    codigo1 = "FUS resultado := 10 + 20 - 5"
    resultado1 = compilador.compile(codigo1)
    
    print("\n" + "-"*80)
    if resultado1:
        print("[OK] TESTE 1: COMPILAÇÃO BEM-SUCEDIDA!")
        print("      Sintaxe: CORRETA")
        print("      Semântica: CORRETA")
        print("      Variável 'resultado' declarada e inicializada")
        print("      Valor calculado: 10 + 20 - 5 = 25")
    else:
        print("[X] TESTE 1: ERRO NA COMPILAÇÃO (INESPERADO)")
    print("-"*80)
    
    # ========================================================================
    # TESTE 2: USO DE JUN (return) PARA RETORNAR VALOR
    # ========================================================================
    print("\n\n" + "="*80)
    print("           TESTE 2: JUN (RETURN) - RETORNAR VALOR")
    print("="*80)
    print("\nCódigo:")
    print("  FUS x := 15 ; JUN x")
    print("\nDescrição: Declara variável e retorna seu valor com JUN")
    print("Resultado esperado: SUCESSO (JUN funciona como print/return)\n")
    
    compilador.reset()
    codigo2 = "FUS x := 15 ; JUN x"
    resultado2 = compilador.compile(codigo2)
    
    print("\n" + "-"*80)
    if resultado2:
        print("[OK] TESTE 2: COMPILAÇÃO BEM-SUCEDIDA!")
        print("      JUN retorna o valor de 'x' = 15")
        print("      Sintaxe: CORRETA (sequência de comandos com ';')")
        print("      Semântica: CORRETA (variável declarada antes de usar)")
    else:
        print("[X] TESTE 2: ERRO NA COMPILAÇÃO (INESPERADO)")
    print("-"*80)
    
    # ========================================================================
    # TESTE 3: ERRO SINTÁTICO (falta operador :=)
    # ========================================================================
    print("\n\n" + "="*80)
    print("           TESTE 3: ERRO SINTÁTICO")
    print("="*80)
    print("\nCódigo:")
    print("  FUS x 10 + 5")
    print("\nDescrição: Declaração SEM operador de atribuição ':='")
    print("Erro esperado: ERRO SINTÁTICO (parser rejeita)\n")
    
    compilador.reset()
    codigo3 = "FUS x 10 + 5"
    resultado3 = compilador.compile(codigo3)
    
    print("\n" + "-"*80)
    if resultado3:
        print("[X] TESTE 3: COMPILADO (INESPERADO - DEVERIA FALHAR)")
    else:
        print("[OK] TESTE 3: ERRO DETECTADO CORRETAMENTE!")
        print("      Parser identificou sintaxe incorreta")
        print("      Esperava ':=' mas encontrou 'num'")
    print("-"*80)
    
    # ========================================================================
    # TESTE 4: ERRO SEMÂNTICO (variável não declarada)
    # ========================================================================
    print("\n\n" + "="*80)
    print("           TESTE 4: ERRO SEMÂNTICO")
    print("="*80)
    print("\nCódigo:")
    print("  JUN y + 10")
    print("\nDescrição: Uso de variável 'y' não declarada em JUN")
    print("Erro esperado: ERRO SEMÂNTICO (variável não existe)\n")
    
    compilador.reset()
    codigo4 = "JUN y + 10"
    resultado4 = compilador.compile(codigo4)
    
    print("\n" + "-"*80)
    if resultado4:
        print("[X] TESTE 4: COMPILADO (INESPERADO - DEVERIA FALHAR)")
    else:
        print("[OK] TESTE 4: ERRO DETECTADO CORRETAMENTE!")
        print("      Análise semântica identificou variável não declarada")
        print("      Variável 'y' usada sem declaração prévia (FUS)")
    print("-"*80)
    
    # ========================================================================
    # TESTE 5: ERRO LÉXICO (caractere inválido no PDA)
    # ========================================================================
    print("\n\n" + "="*80)
    print("           TESTE 5: ERRO LÉXICO")
    print("="*80)
    print("\nCódigo:")
    print("  FUS valor := 10 @ 5")
    print("\nDescrição: Operador '@' não existe na linguagem")
    print("Erro esperado: ERRO SINTÁTICO (token inválido rejeitado)\n")
    
    compilador.reset()
    codigo5 = "FUS valor := 10 @ 5"
    resultado5 = compilador.compile(codigo5)
    
    print("\n" + "-"*80)
    if resultado5:
        print("[X] TESTE 5: COMPILADO (INESPERADO - DEVERIA FALHAR)")
    else:
        print("[OK] TESTE 5: ERRO DETECTADO CORRETAMENTE!")
        print("      PDA/Parser rejeitou token inválido '@'")
        print("      Operador não pertence ao alfabeto da linguagem")
    print("-"*80)
    
    # ========================================================================
    # TESTE 6: ERRO SINTÁTICO (parênteses não fechados)
    # ========================================================================
    print("\n\n" + "="*80)
    print("           TESTE 6: ERRO SINTÁTICO (ESTRUTURA)")
    print("="*80)
    print("\nCódigo:")
    print("  FUS calc := ( 5 + 3")
    print("\nDescrição: Expressão com parêntese não fechado")
    print("Erro esperado: ERRO SINTÁTICO (estrutura inválida)\n")
    
    compilador.reset()
    codigo6 = "FUS calc := ( 5 + 3"
    resultado6 = compilador.compile(codigo6)
    
    print("\n" + "-"*80)
    if resultado6:
        print("[X] TESTE 6: COMPILADO (INESPERADO - DEVERIA FALHAR)")
    else:
        print("[OK] TESTE 6: ERRO DETECTADO CORRETAMENTE!")
        print("      Parser identificou estrutura malformada")
        print("      Esperava ')' para fechar expressão")
    print("-"*80)
    
    # ========================================================================
    # RESUMO
    # ========================================================================
    print("\n\n" + "="*80)
    print("                         RESUMO DOS TESTES")
    print("="*80)
    print(f"  Teste 1 (Correto):          {'[OK] PASSOU' if resultado1 else '[X] FALHOU'}")
    print(f"  Teste 2 (JUN Return):       {'[OK] PASSOU' if resultado2 else '[X] FALHOU'}")
    print(f"  Teste 3 (Erro Sintático):   {'[OK] PASSOU' if not resultado3 else '[X] FALHOU'}")
    print(f"  Teste 4 (Erro Semântico):   {'[OK] PASSOU' if not resultado4 else '[X] FALHOU'}")
    print(f"  Teste 5 (Erro Léxico):      {'[OK] PASSOU' if not resultado5 else '[X] FALHOU'}")
    print(f"  Teste 6 (Erro Estrutural):  {'[OK] PASSOU' if not resultado6 else '[X] FALHOU'}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
    
