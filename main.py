from modelos.matriz import MatrizTPM
from modelos.sistema import Sistema

matriz = MatrizTPM('archivos/matrizGuia.csv')
sistema = Sistema('archivos/estructura.csv')
matriz.eliminar_filas_por_bits(sistema.get_sistema_candidato(), sistema.get_estado_inicial())
matriz.eliminar_columnas_por_bits(sistema.get_sistema_candidato())
matriz.get_matriz()
matriz.marginalizar_filas(sistema.get_subsistema_presente())
matriz.marginalizar_columnas(sistema.get_subsistema_futuro())