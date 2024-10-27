from modelos.matriz import MatrizTPM
from modelos.sistema import Sistema

matriz = MatrizTPM('archivos/matrizGuia.csv')
sistema = Sistema('archivos/estructura.csv')
matriz.condiciones_de_background(sistema.get_sistema_candidato(), sistema.get_estado_inicial())
print(matriz.get_listados())
matriz.marginalizar_subsistema_entrada(sistema.get_subsistema_presente(), sistema.get_subsistema_futuro())
matriz.obtener_estado_nodo()
matriz.get_matriz()