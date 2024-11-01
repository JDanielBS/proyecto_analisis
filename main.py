from modelos.matriz import MatrizTPM
from modelos.sistema import Sistema

matriz = MatrizTPM('archivos/matrizGuia.csv')
sistema = Sistema('archivos/estructura.csv')
matriz.condiciones_de_background()
matriz.get_listados()
# matriz.marginalizar_subsistema_entrada(sistema.get_subsistema_presente(), sistema.get_subsistema_futuro())
matriz.obtener_estado_nodo()
print(matriz.get_diccionario())
matriz.get_matriz()
# matriz.prueba_producto_tensorial()
matriz.prueba_marginalizar()
# matriz.prueba_lista()