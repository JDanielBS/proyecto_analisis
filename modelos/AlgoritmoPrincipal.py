from modelos.matriz import MatrizTPM
from icecream import ic
from modelos.Emd import Emd
import numpy as np


class AlgoritmoPrincipal:
    def __init__(self, ruta):
        self.__matriz = MatrizTPM(ruta)
        self.__emd = Emd()

    def estrategia1(self):
        self.__matriz.condiciones_de_background()
        self.__matriz.obtener_estado_nodo()
        # ic(self.__matriz.get_diccionario())
        self.__matriz.matriz_subsistema()
        # ic(self.__matriz.get_dic_marginalizadas())
        self.__matriz.get_matriz_subsistema()
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
        mejor_particion = []
        for i in range(len(V) - 1):
            mejor_iteracion = ()
            for j in list(set(V) - set(W)):
                ic(j)
                subsistema = []
                u = []
                self.add_elements_to_list(subsistema, v1)
                self.add_elements_to_list(subsistema, j)
                self.add_elements_to_list(u, j)
                ic(subsistema)
                ic(u)

                print("SE HACE LA V1 U U")
                ic(subsistema)
                matriz_normal, matriz_complemento = self.__matriz.marginalizar_normal_complemento(subsistema)
                est_n, est_c = self.__matriz.get_estado_inicial_n_c()
                self.__matriz.limpiar_estados_inicialies()
                resultado_tensorial = self.__matriz.producto_tensorial_matrices(matriz_normal[0], matriz_complemento[0], matriz_normal[1], matriz_complemento[1], est_n, est_c)
                resultados_lista = np.array(resultado_tensorial.iloc[0].values.tolist())
                resultadoEMD= self.__emd.calcularEMD(resultados_lista, self.__matriz.get_matriz_subsistema())

                print("SE HACE EL U")
                matriz_nu, matriz_complemento_nu = self.__matriz.marginalizar_normal_complemento(u)
                est_n, est_c = self.__matriz.get_estado_inicial_n_c()
                self.__matriz.limpiar_estados_inicialies()
                resultado_tensorial_nu = self.__matriz.producto_tensorial_matrices(matriz_nu[0], matriz_complemento_nu[0], matriz_nu[1], matriz_complemento_nu[1], est_n, est_c)
                resultados_lista_nu = np.array(resultado_tensorial_nu.iloc[0].values.tolist())
                resultadoEMD_nu= self.__emd.calcularEMD(resultados_lista_nu, self.__matriz.get_matriz_subsistema())

                resultado = resultadoEMD - resultadoEMD_nu
                ic(resultado)

                if mejor_iteracion == ():
                    mejor_iteracion = (resultado, j)
                elif resultado < mejor_iteracion[0]:
                    mejor_iteracion = (resultado, j)
            
            W.append(mejor_iteracion[1])
            ic(W)

    def add_elements_to_list(self, lista, element):
        if isinstance(element, list):
            lista.extend(element)
        else:
            lista.append(element)
        return lista
