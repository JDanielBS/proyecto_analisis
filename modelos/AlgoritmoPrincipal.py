from modelos.matriz import MatrizTPM
from icecream import ic

class AlgoritmoPrincipal:
    def __init__(self):
        self.__matriz = MatrizTPM('archivos/matrizGuia.csv')

    def estrategia1(self):
        self.__matriz.condiciones_de_background()
        self.__matriz.obtener_estado_nodo()
        # print(self.__matriz.get_diccionario())
        self.__matriz.obtener_vector_subsitema_teorico()
        self.encontrar_particion_menor()

    def encontrar_particion_menor(self):
        conjuntoV = self.__matriz.pasar_cadena_a_lista()
        ic(conjuntoV)
        self.algoritmo_principal(conjuntoV)

    # TODO: verificar cuando es vacío en presente o en futuro
    def algoritmo_principal(self, V):
        if(len(V) == 2):
            return
        v1 = V[0]
        ic(v1)
        W = [v1]

        for i in range(len(V) - 1):
            for j in list(set(V) - set(W)):
                ic(j)
                subsistema = []
                if isinstance(v1, list) and isinstance(j, list):
                    subsistema.extend(v1)
                    subsistema.extend(j)
                elif isinstance(v1, list):
                    subsistema.extend(v1)
                    subsistema.append(j)
                elif isinstance(j, list):
                    subsistema.append(v1)
                    subsistema.extend(j)
                else:
                    subsistema.append(v1)
                    subsistema.append(j)
                ic(subsistema)
                #(0, 0), (1, 0)
                matriz_normal = self.__matriz.marginalizar(subsistema, '0')
                matriz_complemento = self.__matriz.marginalizar(subsistema, '1')
                print('Matriz normal', matriz_normal)
                print('Matriz complemento', matriz_complemento)