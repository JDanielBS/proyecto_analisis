from modelos.matriz import MatrizTPM
from icecream import ic
from modelos.Emd import Emd

class AlgoritmoPrincipal:
    def __init__(self):
        self.__matriz = MatrizTPM('archivos/matrizGuia.csv')
        self.__emd = Emd()

    def estrategia1(self):
        self.__matriz.condiciones_de_background()
        self.__matriz.obtener_estado_nodo()
        # ic(self.__matriz.get_diccionario())
        self.__matriz.matriz_subsistema()
        # ic(self.__matriz.get_dic_marginalizadas())
        self.encontrar_particion_menor()

    def encontrar_particion_menor(self):
        conjuntoV = self.__matriz.pasar_cadena_a_lista()
        ic(conjuntoV)
        self.algoritmo_principal(conjuntoV)

    def algoritmo_principal(self, V):
        if(len(V) == 2):
            return
        v1 = V[0]
        ic(v1)
        W = [v1]
        ic(W)
        ic(V)
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

                matriz_normal, matriz_complemento = self.__matriz.marginalizar_normal_complemento(subsistema)
                resultado_tensorial = self.__matriz.producto_tensorial_matrices(matriz_normal[0], matriz_complemento[0], matriz_normal[1], matriz_complemento[1])
                resultados_lista = resultado_tensorial.iloc[0].values.tolist()
                ic(resultados_lista)