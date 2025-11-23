# Analisador Sintático SLR(1) com Análise Semântica

## 📋 Descrição do Projeto

Sistema completo de compilação para linguagem de programação com palavras-chave inspiradas em The Elder Scrolls (Skyrim). O compilador implementa três fases de análise:

1. **Análise Léxica (PDA)** - Autômato de Pilha
2. **Análise Sintática (SLR)** - Parser Bottom-Up SLR(1)
3. **Análise Semântica** - Tabela de Símbolos e Validações

---

## 🚀 Execução Rápida

```powershell
# Executar testes de validação
python main.py

# Ver exemplos completos com todas as palavras-chave
python apresentacao.py
```

---

## 📦 Estrutura de Arquivos

### Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `main.py` | **Pipeline completo** - Integra PDA → Parser → Semântica |
| `parser_integrated.py` | **Parser SLR(1)** com análise semântica integrada |
| `symbol_table.py` | **Tabela de símbolos** - Gerencia declarações e escopos |
| `lexer.py` | Analisador léxico alternativo (tokenização tradicional) |

### Arquivos de Configuração

| Arquivo | Descrição |
|---------|-----------|
| `SLR.py` | 60 estados (closures) do autômato LR(0) |
| `goto.py` | Tabela GOTO com 200+ transições de estados |
| `terminais.py` | 23 símbolos terminais da gramática |
| `nao_terminais.py` | 11 símbolos não-terminais da gramática |
| `first.py` | Conjuntos FIRST para análise preditiva |
| `follow.py` | Conjuntos FOLLOW para decisões de redução |
| `regrasSintáticas.txt` | Gramática BNF com 25 produções |

### Módulo PDA (Compiladores/)

| Arquivo | Descrição |
|---------|-----------|
| `Compiladores/pda.py` | Implementação do autômato de pilha |
| `Compiladores/delta.py` | Função de transição δ do PDA |
| `Compiladores/constants.py` | Constantes (epsilon, etc) |
| `Compiladores/main.py` | Testes originais do PDA |

---

## 🔑 Palavras-Chave da Linguagem

### Comandos Principais

| Keyword | Significado | Exemplo |
|---------|-------------|---------|
| `FUS` | Declaração de variável | `FUS x := 10` |
| `assign` | Atribuição | `assign x := 20` |
| `LOS` | Condicional (if) | `LOS x CMD` |
| `FOD ... FAH` | Loop while | `FOD CMD FAH EXPR` |
| `FAH ... FAH` | Loop for | `FAH CMD FAH EXPR` |
| `JUN` | Return | `JUN x + 5` |
| `KEL` | Módulo/Escopo | `KEL player CMD` |

### Operações

| Keyword | Significado | Exemplo |
|---------|-------------|---------|
| `HON` | Input | `HON x` |
| `print` | Output | `print resultado` |
| `HIM` | Acesso a atributo (this.) | `HIM . valor` |
| `NUST` | Negação lógica (not) | `NUST x` |
| `ANRK` | E lógico (and) | `x ANRK y` |
| `AAN` | Ou lógico (or) | `x AAN y` |
| `KO` | Pertence (in) | `x KO lista` |

---

## 📚 Classes e Funções Importantes

### 1. `PDALexerAdapter` (main.py)

**Propósito**: Adapta saída do PDA para gerar tokens compatíveis com parser SLR

#### Métodos Principais

```python
def __init__(self):
    """
    Inicializa PDA com 36 estados e 12 estados finais
    Configura mapeamento: estado final → tipo de token
    """

def tokenize(self, source_code: str) -> List[Token]:
    """
    Executa análise léxica completa
    
    Args:
        source_code: Código fonte (ex: "FUS x := 10")
    
    Returns:
        Lista de tokens: [Token(FUS), Token(id,'x'), Token(:=), Token(num,10), Token($)]
    
    Processo:
        1. Divide entrada por linhas (delimitador '#')
        2. Processa cada palavra com PDA
        3. Mapeia estados finais para tokens
        4. Classifica palavras não reconhecidas (ID, NUM, operadores)
        5. Adiciona EOF ($)
    """

def _reconhecer_palavra(self, palavra: str) -> str:
    """
    Simula reconhecimento de palavra pelo PDA
    
    Returns:
        Estado final (ex: 'D5,Z' para FUS) ou 'X' (rejeitado)
    """

def _classificar_palavra_desconhecida(self, palavra: str, linha: int) -> Token:
    """
    Classifica tokens não reconhecidos pelo PDA
    
    Casos:
        - Números: Token(num)
        - Operadores: :=, +, -, ;, ., (, )
        - Keywords extras: assign, print
        - Padrão: Token(id) para identificadores
    """
```

#### Mapeamento de Estados

```python
STATE_TO_TOKEN = {
    'E11,Z': 'KEL',   # Módulo
    'D10,Z': 'LOS',   # If
    'E12,Z': 'FOD',   # While
    'D3,Z': 'FAH',    # Separador
    'D5,Z': 'FUS',    # Declaração
    'D9,Z': 'HON',    # Input
    'D4,Z': 'JUN',    # Return
    'D6,Z': 'HIM',    # This
    'D7,Z': 'NUST',   # Not
    'D8,Z': 'ANRK',   # And
    'D2,Z': 'AAN',    # Or
    'B1,Z': 'KO',     # In
}
```

---

### 2. `CompiladorCompleto` (main.py)

**Propósito**: Orquestra pipeline completo de compilação

#### Métodos Principais

```python
def __init__(self, verbose=True):
    """
    Inicializa compilador com:
        - PDALexerAdapter (fase léxica)
        - SLRParserWithSemantics (fases sintática + semântica)
    """

def compile(self, source_code: str) -> bool:
    """
    Executa compilação completa em 3 fases
    
    Args:
        source_code: Código fonte completo
    
    Returns:
        True se compilação bem-sucedida, False se erros detectados
    
    Fases:
        FASE 1: Análise Léxica (PDA)
            - Tokenização via PDA
            - Geração de tabela de símbolos do PDA
        
        FASE 2: Análise Sintática (SLR)
            - Validação de estrutura com parser SLR(1)
            - Ações shift/reduce
            - Detecção de erros sintáticos
        
        FASE 3: Análise Semântica (integrada)
            - Verificação de declarações
            - Validação de uso de variáveis
            - Detecção de redeclarações
            - Avisos de variáveis não usadas
    """

def reset(self):
    """
    Reinicia estado do compilador
    Limpa tabela de símbolos e erros acumulados
    """
```

---

### 3. `SLRParserWithSemantics` (parser_integrated.py)

**Propósito**: Parser SLR(1) com análise semântica integrada

#### Métodos Principais

```python
def __init__(self, verbose=True):
    """
    Inicializa parser com:
        - Pilha de estados: [0]
        - Pilha de símbolos sintáticos: []
        - Pilha de atributos semânticos: []
        - Tabela de símbolos: SymbolTable()
        - Listas de erros e avisos
    """

def parse(self, tokens: List[Token]) -> bool:
    """
    Executa parsing SLR(1) com ações semânticas
    
    Algoritmo:
        1. SHIFT: Empilha estado e token
        2. REDUCE: 
            - Aplica produção da gramática
            - Executa ação semântica
            - Faz GOTO para próximo estado
        3. ACCEPT: Aceita quando estado=1 e lookahead=$
        4. ERROR: Registra erro e tenta recuperação
    
    Returns:
        True se aceito sem erros, False caso contrário
    """

def semantic_action(self, lhs: str, rhs: List[str], attributes: List) -> Any:
    """
    Executa ações semânticas durante redução
    
    Produções Tratadas:
        
        CMD -> FUS id := EXPR
            - Declara variável com valor inicial
            - Adiciona à tabela de símbolos
            - Erro se redeclaração
        
        CMD -> LHS := EXPR
            - Atribuição a variável existente
            - Valida se variável foi declarada
        
        CMD -> JUN EXPR
            - Comando return
            - Valida variáveis usadas na expressão
        
        FACTOR -> id
            - Uso de variável
            - Valida se foi declarada (erro semântico)
            - Marca variável como usada
        
        EXPR -> TERM EXPR'
            - Avalia expressões aritméticas
            - Propaga valores (quando possível)
    
    Returns:
        Atributo sintetizado (valor, tipo, etc)
    """

def print_report(self):
    """
    Exibe relatório final de compilação
    
    Conteúdo:
        - Erros sintáticos (com linha e contexto)
        - Erros semânticos (variáveis não declaradas)
        - Avisos (variáveis declaradas mas não usadas)
        - Tabela de símbolos (todas as variáveis declaradas)
        - Status final: SUCESSO ou FALHA
    """
```

---

### 4. `SymbolTable` (symbol_table.py)

**Propósito**: Gerencia símbolos e escopos durante análise semântica

#### Classes

```python
class Symbol:
    """
    Representa um identificador
    
    Atributos:
        name: Nome do identificador
        symbol_type: 'variable', 'module', 'parameter'
        scope: Escopo onde foi declarado
        line: Linha de declaração (para mensagens de erro)
        value: Valor inicial (opcional)
        used: Flag indicando se foi referenciado
    """

class Scope:
    """
    Representa um escopo (bloco de código)
    
    Atributos:
        name: Nome do escopo ('global', 'KEL_player', etc)
        parent: Escopo pai (para aninhamento)
        symbols: Dicionário de símbolos {nome: Symbol}
        children: Lista de escopos filhos
    """

class SymbolTable:
    """Gerenciador de tabela de símbolos com escopos aninhados"""
```

#### Métodos Principais

```python
def __init__(self):
    """
    Inicializa com escopo global
    Cria pilha de escopos ativos
    """

def declare(self, name: str, symbol_type: str, line: int, value=None) -> bool:
    """
    Declara novo símbolo no escopo atual
    
    Args:
        name: Nome do identificador
        symbol_type: Tipo ('variable', 'module')
        line: Linha de declaração
        value: Valor inicial (opcional)
    
    Returns:
        True se declarado com sucesso
        False se já existe no escopo atual (redeclaração)
    
    Exemplo:
        symbol_table.declare('x', 'variable', 5, 10)  # FUS x := 10
    """

def lookup(self, name: str, line: int = None) -> Symbol:
    """
    Busca símbolo nos escopos (atual → pais)
    
    Args:
        name: Nome do identificador
        line: Linha de uso (para mensagens de erro)
    
    Returns:
        Symbol encontrado ou None
        
    Marca símbolo como usado quando encontrado
    """

def enter_scope(self, name: str):
    """
    Entra em novo escopo (para KEL, loops, etc)
    
    Args:
        name: Nome do escopo
    """

def exit_scope(self):
    """
    Sai do escopo atual, retorna ao pai
    """

def check_unused_symbols(self) -> List[str]:
    """
    Verifica símbolos declarados mas nunca usados
    
    Returns:
        Lista de mensagens de aviso
    
    Exemplo:
        ["Line 3: Variable 'temp' declared but never used"]
    """

def get_all_symbols(self) -> List[Symbol]:
    """
    Retorna todos os símbolos de todos os escopos
    Para exibição em relatórios
    """
```

---

### 5. `Token` (parser_integrated.py)

**Propósito**: Representa um token com informações completas

```python
class Token:
    """
    Token com atributos para análise léxica e semântica
    
    Atributos:
        type: Tipo do token ('FUS', 'id', 'num', ':=', etc)
        lexeme: Texto literal ('resultado', '10', 'FUS')
        line: Número da linha no código fonte
        column: Coluna no código fonte (opcional)
        value: Valor semântico (int para num, str para id)
    """
    
    def __init__(self, token_type, lexeme, line, column=0, value=None):
        self.type = token_type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', L{self.line})"
```

---

## 🎯 Gramática da Linguagem

### Produções Principais

```
S' -> S                           (Axioma aumentado)

S ::= CMD ; S                     (Sequência de comandos)
    | CMD                         (Comando único)

CMD ::= FUS id := EXPR            (Declaração com atribuição)
     | LHS := EXPR                (Atribuição)
     | LOS EXPR CMD               (Condicional if)
     | FOD CMD FAH EXPR           (Loop while)
     | FAH CMD FAH EXPR           (Loop for)
     | IO id                      (Input/Output)
     | JUN EXPR                   (Return)
     | KEL id CMD                 (Módulo/Escopo)

LHS ::= assign id                (Atribuição simples)
      | HIM . id                 (Atribuição de atributo)

EXPR ::= TERM EXPR'              (Expressões)

EXPR' ::= OP TERM EXPR'          (Operações binárias)
        | ε                      (Vazio)

OP ::= + | - | ANRK | AAN | KO   (Operadores)

TERM ::= UNARY | FACTOR          (Termos)

UNARY ::= NUST TERM              (Negação)

FACTOR ::= id                    (Identificador)
         | num                   (Número)
         | HIM . id              (Atributo)
         | ( EXPR )              (Expressão parentizada)

IO ::= HON | print               (Input/Output)
```

### Conjuntos FIRST e FOLLOW

Usados para decisões de parsing:

- **FIRST**: Terminais que podem iniciar uma produção
- **FOLLOW**: Terminais que podem seguir um não-terminal

---

## 🧪 Exemplos de Uso

### Exemplo 1: Declaração Simples

```python
codigo = "FUS x := 10"
compilador = CompiladorCompleto(verbose=False)
resultado = compilador.compile(codigo)

# Saída:
# [OK] PDA reconheceu 'FUS' -> Estado D5,Z -> FUS
# [OK] Variável 'x' declarada com valor 10
# [OK] COMPILAÇÃO BEM-SUCEDIDA
```

### Exemplo 2: Expressão Aritmética

```python
codigo = "FUS resultado := 10 + 20 - 5"
compilador.compile(codigo)

# Saída:
# [OK] Tokens: FUS, id('resultado'), :=, num(10), +, num(20), -, num(5), $
# [OK] Parser: FUS id := EXPR
# [OK] Semântica: resultado = 25
# [OK] Símbolo 'resultado' adicionado à tabela
```

### Exemplo 3: Uso de JUN (Return)

```python
codigo = "FUS x := 15 ; JUN x"
compilador.compile(codigo)

# Saída:
# [OK] Declaração: x = 15
# [OK] Return: JUN retorna valor de x
# [OK] Sequência de comandos (;) reconhecida
```

### Exemplo 4: Erro Sintático

```python
codigo = "FUS x 10 + 5"  # Falta :=
compilador.compile(codigo)

# Saída:
# [X] ERRO SINTÁTICO (Linha 1)
# [X] Esperava ':=' mas encontrou 'num'
# [X] Estado: 9, Token: num
```

### Exemplo 5: Erro Semântico

```python
codigo = "assign total := y + 10"  # 'y' não declarado
compilador.compile(codigo)

# Saída:
# [OK] Sintaxe correta
# [X] ERRO SEMÂNTICO (Linha 1)
# [X] Variável 'y' usada sem declaração
# [X] Use 'FUS y := valor' para declarar
```

---

## 📊 Fluxo de Compilação

```
┌─────────────────────────────────────────────────┐
│  CÓDIGO FONTE: "FUS x := 10 + 5"               │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  FASE 1: ANÁLISE LÉXICA (PDA)                  │
│  ─────────────────────────────                  │
│  • Entrada processada caractere por caractere   │
│  • PDA reconhece palavras-chave                 │
│  • Classificação de tokens não reconhecidos     │
│  • Saída: [FUS, id, :=, num, +, num, $]        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  FASE 2: ANÁLISE SINTÁTICA (SLR)               │
│  ──────────────────────────────                 │
│  • Parser SLR(1) valida estrutura               │
│  • Pilha: [0] → [0,5,9,16,...]                  │
│  • Ações: SHIFT, REDUCE, GOTO                   │
│  • Produção reconhecida: CMD -> FUS id := EXPR  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  FASE 3: ANÁLISE SEMÂNTICA                     │
│  ────────────────────────                       │
│  • Ação: Declarar variável 'x'                  │
│  • Avaliar: 10 + 5 = 15                         │
│  • Tabela: {'x': Symbol(variable, global, 15)} │
│  • Validações: ✓ Sem redeclarações             │
│                ✓ Sem uso indevido               │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  RESULTADO FINAL                                │
│  ───────────────                                │
│  [OK] COMPILAÇÃO BEM-SUCEDIDA                   │
│  • 0 Erros Sintáticos                           │
│  • 0 Erros Semânticos                           │
│  • 0 Avisos                                     │
│  • Tabela de Símbolos: 1 símbolo               │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Detecção de Erros

### Tipos de Erros Detectados

#### 1. Erros Léxicos
- Caracteres inválidos no alfabeto
- Tokens malformados

```python
"FUS x := 10 @ 5"  # '@' não reconhecido
# Erro: Caractere '@' não pertence ao alfabeto
```

#### 2. Erros Sintáticos
- Estrutura inválida
- Tokens inesperados
- Falta de símbolos obrigatórios

```python
"FUS x 10"  # Falta ':='
# Erro: Esperava ':=' mas encontrou 'num'

"FUS calc := ( 5 + 3"  # Parêntese não fechado
# Erro: Esperava ')' mas encontrou '$'
```

#### 3. Erros Semânticos
- Variável não declarada
- Redeclaração de variável
- Uso antes de declaração

```python
"assign total := y + 10"  # 'y' não existe
# Erro: Variável 'y' usada sem declaração prévia

"FUS x := 5 ; FUS x := 10"  # Redeclaração
# Erro: Variável 'x' já foi declarada (linha 1)
```

#### 4. Avisos (Warnings)
- Variável declarada mas nunca usada

```python
"FUS temp := 10"  # 'temp' não é usado depois
# Aviso: Variável 'temp' declarada mas nunca usada
```

---

## 🛠️ Testes Automatizados

Execute `python main.py` para executar suite de 6 testes:

| Teste | Código | Tipo | Resultado Esperado |
|-------|--------|------|-------------------|
| 1 | `FUS resultado := 10 + 20 - 5` | Correto | ✅ Sucesso |
| 2 | `FUS x := 15 ; JUN x` | Correto (JUN) | ✅ Sucesso |
| 3 | `FUS x 10 + 5` | Erro Sintático | ❌ Falta `:=` |
| 4 | `JUN y + 10` | Erro Semântico | ❌ `y` não declarado |
| 5 | `FUS valor := 10 @ 5` | Erro Léxico | ❌ Token `@` inválido |
| 6 | `FUS calc := ( 5 + 3` | Erro Estrutural | ❌ `)` faltando |

---

## 📖 Referências Técnicas

### Algoritmo SLR(1)

O parser implementa o algoritmo **Simple LR (SLR)**, um parser bottom-up que:

1. **Constrói autômato LR(0)** com 60 estados (closures)
2. **Usa tabela GOTO** para transições entre estados
3. **Consulta FOLLOW** para decidir reduções
4. **Resolve conflitos** usando lookahead de 1 token

### Tabela de Parsing

```
Estado | Token | Ação
-------|-------|----------------
   0   | FUS   | SHIFT → 5
   5   | id    | SHIFT → 9
   9   | :=    | SHIFT → 16
  16   | num   | SHIFT → 22
  22   | +     | SHIFT → 28
  ...  | ...   | ...
```

### Produções da Gramática

Total: **25 produções** distribuídas em:
- 11 não-terminais
- 23 terminais
- Gramática livre de contexto (CFG)
- Sem ambiguidades

---

## 👥 Autores e Licença

**Projeto desenvolvido para disciplina de Compiladores**

- Implementação de PDA para reconhecimento de palavras-chave
- Parser SLR(1) com tabela de símbolos
- Análise semântica integrada
- Sistema completo de tratamento de erros

---

## 🎓 Conceitos Aplicados

- ✅ Teoria de Autômatos (PDA)
- ✅ Análise Sintática (SLR Parser)
- ✅ Análise Semântica (Symbol Table)
- ✅ Tratamento de Erros
- ✅ Compilação em Múltiplas Fases
- ✅ Gramáticas Livres de Contexto
- ✅ Conjuntos FIRST/FOLLOW
- ✅ Escopos Aninhados
- ✅ Atributos Sintetizados

---

## 📞 Contato e Suporte

Para dúvidas sobre o funcionamento do compilador:

1. Consulte os exemplos em `main.py`
2. Execute `python apresentacao.py` para demonstração completa
3. Verifique a gramática em `regrasSintáticas.txt`
4. Analise os estados em `SLR.py` e transições em `goto.py`

---

**Última atualização**: 22 de novembro de 2025
