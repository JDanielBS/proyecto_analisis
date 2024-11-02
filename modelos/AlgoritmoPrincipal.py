from modelos.matriz import MatrizTPM

class AlgoritmoPrincipal:
    def __init__(self):
        self.__matriz = MatrizTPM('archivos/matrizGuia.csv')

    def estrategia1(self):
        self.__matriz.condiciones_de_background()
        self.__matriz.obtener_estado_nodo()
        print(self.__matriz.get_diccionario())
        self.__matriz.obtener_vector_subsitema_teorico()
        self.encontrar_particion_menor()

    def encontrar_particion_menor(self):
        conjuntoV = [[0,0]]

    def algoritmo_principal(self):
        pass
    