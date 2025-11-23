from Compiladores.pda import AP
from Compiladores.constants import EPSILON
from Compiladores.delta import DeltaFinal

# Definição do autômato de pilha
Q = ['A1,B2,Z', 'Z', 'B7,B8,Z', 'B3,B6,Z',
	  'B12,Z', 'B4,Z', 'B5,B9,Z', 'B10,B11,Z',
	  'B1,Z', 'C2,Z', 'C8,Z', 'C7,Z',
	  'B3,Z', 'C6,Z', 'C12,Z', 'C4,Z',
	  'C9,Z', 'C5,Z', 'B11,Z', 'B10,Z',
	  'D2,Z', 'D8,Z', 'D7,Z', 'C3,Z',
	  'D6,Z', 'D12,Z', 'D4,Z', 'D9,Z',
	  'D5,Z', 'C11,Z', 'C10,Z', 'D3,Z',
	  'E12,Z', 'D11,Z', 'D10,Z', 'E11,Z']

Sigma = ['#', 'K', 'O', 'E', 
		 'L', 'H', 'N', 'J', 
		 'U', 'F', 'S', 'I', 
		 'M', 'D', 'R', 'T', 
		 'A', EPSILON]

gama = ['$', 'K', 'O', 'E', 
		 'L', 'H', 'N', 'J', 
		 'U', 'F', 'S', 'I', 
		 'M', 'D', 'R', 'T', 
		 'A', EPSILON]

delta = DeltaFinal  

F = ['E11,Z', 'D10,Z', 'E12,Z', 'D3,Z', 
	 'D5,Z', 'D9,Z', 'D10,Z', 'D4,Z', 'D6,Z',
	 'D7,Z', 'D8,Z', 'D2,Z', 'B1,Z']

# Criação do autômato de pilha
pda = AP( Sigma, gama, delta, 'S', F)



nova_sequencia_testes = [
						 "KO KEL # LOS",
						 "# FAH # HIM # JUN #",
						 " FOD # FUS # HON # NUST AAN ANRK",
						 "FUS ROH DAH"]

for entrada in nova_sequencia_testes:
	resultado = pda.run(entrada)
	print(f"Entrada: {entrada} ")