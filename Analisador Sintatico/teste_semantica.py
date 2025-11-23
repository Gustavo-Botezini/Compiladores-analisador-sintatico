# -*- coding: utf-8 -*-
"""
TESTE SIMPLES DE DETECCAO DE ERROS SEMANTICOS
Usa o compilador_completo.py que ja esta funcionando
"""

from compilador_completo import compilar


def linha(char="=", tam=80):
    print(char * tam)


def teste(numero, descricao, codigo, deve_ter_erro=False):
    """Testa um codigo"""
    print("\n")
    linha("=")
    print(f"EXEMPLO {numero}: {descricao}".center(80))
    linha("=")
    print(f"\nCodigo:\n{codigo}\n")
    linha("-")
    
    # Compilar (retorna tupla: sucesso, lexer, parser)
    sucesso, lexer, parser = compilar(codigo, verbose=False, mostrar_tokens=False)
    
    print("\n")
    linha("-")
    
    if deve_ter_erro:
        # Se esperamos erro, sucesso deve ser False OU deve ter erros semanticos
        tem_erro = not sucesso or (parser and parser.symbol_table.errors)
        if tem_erro:
            print("[OK] Erro DETECTADO corretamente!")
            return True
        else:
            print("[FALHA] Deveria ter detectado erro mas nao detectou!")
            return False
    else:
        # Se NAO esperamos erro, sucesso deve ser True E sem erros semanticos
        sem_erro = sucesso and (not parser or not parser.symbol_table.errors)
        if sem_erro:
            print("[OK] Codigo aceito!")
            return True
        else:
            print("[FALHA] Codigo correto foi rejeitado!")
            return False


def main():
    print("\n\n")
    linha("=")
    print("TESTE DE ANALISE SEMANTICA - DETECCAO AUTOMATICA DE ERROS".center(80))
    linha("=")
    
    # =========================================================================
    # TESTE 1: CODIGO CORRETO
    # =========================================================================
    codigo1 = "FUS health := 100"
    resultado1 = teste(1, "CODIGO CORRETO", codigo1, deve_ter_erro=False)
    
    input("\n>>> Pressione ENTER para proximo teste...")
    
    # =========================================================================
    # TESTE 2: ERRO - VARIAVEL NAO DECLARADA
    # =========================================================================
    codigo2 = "assign mana := 50"
    resultado2 = teste(2, "ERRO: Variavel NAO DECLARADA", codigo2, deve_ter_erro=True)
    
    input("\n>>> Pressione ENTER para proximo teste...")
    
    # =========================================================================
    # TESTE 3: CODIGO CORRETO COM USO DE VARIAVEL
    # =========================================================================
    codigo3 = "FUS x := 10"
    resultado3 = teste(3, "CODIGO CORRETO: Apenas Declaracao", codigo3, deve_ter_erro=False)
    
    input("\n>>> Pressione ENTER para proximo teste...")
    
    # =========================================================================
    # TESTE 4: ERRO - VARIAVEL NAO DECLARADA EM I/O
    # =========================================================================
    codigo4 = "HON player"
    resultado4 = teste(4, "ERRO: I/O com Variavel Nao Declarada", codigo4, deve_ter_erro=True)
    
    # =========================================================================
    # RESUMO
    # =========================================================================
    print("\n\n")
    linha("=")
    print("RESUMO DOS TESTES".center(80))
    linha("=")
    print()
    
    testes = [
        ("Teste 1 - Codigo correto", resultado1),
        ("Teste 2 - Variavel nao declarada", resultado2),
        ("Teste 3 - Declaracao e uso", resultado3),
        ("Teste 4 - Uso antes declaracao", resultado4)
    ]
    
    for nome, resultado in testes:
        status = "[OK]" if resultado else "[FALHA]"
        print(f"  {status} {nome}")
    
    print()
    
    total = sum(1 for _, r in testes if r)
    print(f"Resultado Final: {total}/{len(testes)} testes passaram")
    
    if total == len(testes):
        print("\n*** TODOS OS TESTES PASSARAM! Sistema detecta erros corretamente! ***")
    else:
        print(f"\n*** {len(testes) - total} teste(s) falharam ***")
    
    print()
    linha("=")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste interrompido!\n")
    except Exception as e:
        print(f"\n\nERRO: {e}\n")
        import traceback
        traceback.print_exc()
