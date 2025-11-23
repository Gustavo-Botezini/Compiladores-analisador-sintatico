from collections import deque
from Compiladores.constants import EPSILON
class AP:
    def __init__(self,  Sigma, gama, delta, q0, F):
        self._Sigma = Sigma
        self._gama = gama
        self._delta = delta
        self._q0 = q0
        self._F = F
        self.qA = q0

    def run(self, entrada):
        # Inicializar estruturas
        FITA = []
        TS = []  # Tabela de símbolos: (linha, label, estado_final)
        linha_atual = 0
        
        # Primeiro, separar por '#' (quebras de linha) e depois por '$' (final)

        
        # separar a entrada por '#' (cada # representa uma nova linha)
        linhas = entrada.split('#')
        
        for linha in linhas:
            linha = linha.strip()  
            if not linha:  
                continue
                
            linha_atual += 1
            
            palavras = linha.split(' ')
            
            for palavra in palavras:
                palavra = palavra.strip()  
                if not palavra: 
                    continue
                
                # 1. estadoInicial = q0 (Estado Corrente = q0) - VOLTA PARA INICIAL A CADA PALAVRA
                estadoInicial = self._q0
                #print(f"\n  === Processando palavra '{palavra}' ===")
                #print(f"  Estado inicial: {estadoInicial}")
                
                # 2. Ler(simbolo) - palavra atual
                simbolo = palavra
                
                # 4. Verificar se existe transição para esta palavra
                # Vamos procurar transições baseadas na palavra completa
                transicao_encontrada = False
                
                
                # Se não encontrou, tentar processar caractere por caractere dentro da palavra
                if not transicao_encontrada:
                    #print(f"  Processando palavra '{simbolo}' caractere por caractere:")
                    palavra_valida = True
                    caminhoPalavra = [estadoInicial]  # Armazenar o caminho da palavra

                    for caractere in simbolo:
                        if caractere not in self._Sigma:
                            #print(f"    Caractere '{caractere}' não pertence ao alfabeto Sigma")
                            palavra_valida = False
                            break
                        
                        transicao = self._delta.get((estadoInicial, caractere, EPSILON))
                        if transicao:
                            EC_anterior = estadoInicial
                            estadoInicial = transicao[0]
                            caminhoPalavra.append(estadoInicial)  # Adicionar novo estado ao caminho
                            #print(f"    '{caractere}': {EC_anterior} -> {estadoInicial}")
                        else:
                            #print(f"    '{caractere}': Transição não encontrada para ({estadoInicial}, {caractere})")
                            palavra_valida = False
                            break
                    
                    if not palavra_valida:
                        #print(f"  Palavra '{simbolo}' inválida, indo para estado X")
                        estadoInicial = 'X'
                        caminhoPalavra = [self._q0, 'X']  
                        
                    caminho_str = " -> ".join(caminhoPalavra)
                    #print(f"  Caminho completo: {caminho_str}")
                
                #print(f"  Estado final da palavra '{palavra}': {estadoInicial}")
                
                # 6. se estado não final estadoInicial = X
                if estadoInicial not in self._F:
                    #print(f"  Estado {estadoInicial} não é final para a palavra, mudando para X")
                    estadoInicial = 'X'
                    # Atualizar caminho para mostrar que foi rejeitado
                    if 'caminhoPalavra' in locals():
                        caminhoPalavra[-1] = 'X'  # Substituir último estado por X
                    else:
                        caminhoPalavra = [self._q0, 'X']  # Caminho padrão para erro
                
                if 'caminhoPalavra' in locals():
                    caminho_str = " -> ".join(caminhoPalavra)
                else:
                    caminho_str = f"{self._q0} -> {estadoInicial}"
                
                # 7. add FITA(caminho completo)
                FITA.append(caminho_str)
                # 8. Add TS(linha, caminho, label)
                caminho_dividido = caminho_str.split(" -> ")
                TS.append((linha_atual, caminho_dividido[-1], palavra))
                
                #print(f"  ROTA: Linha {linha_atual}, Palavra '{palavra}' -> Caminho: {caminho_str}")
                
                # 5. vai para 2 (continua o loop) - próxima palavra volta para estado S
            
            #print(f"\n--- Fim da LINHA {linha_atual} ---")
            #print(f"Palavras processadas na linha {linha_atual}: {len([p for p in palavras if p.strip()])}")
        
        # Imprimir resultados finais
        print(f"{'='*50}")
        print("FITA (Caminhos Completos):", FITA)
        print("\nTabela de Simbolos (TS):")
        for i, (linha, caminho, palavra) in enumerate(TS):
            print(f"  {i+1}. Linha {linha}: '{palavra}' -> {caminho}")
        
        print(f"\nTotal de linhas processadas: {linha_atual}")
        print(f"Total de palavras processadas: {len(FITA)}")
        
        # Retorna True se todos os caminhos terminam em estados válidos (não X)
        resultado = all(not caminho.endswith('X') for caminho in FITA)
        return resultado   