import time
from modelos.matriz import MatrizTPM
from icecream import ic
from modelos.MetricasDistancia import MetricasDistancia
import numpy as np


class AlgoritmoPrincipal:
    def __init__(self, ruta):
        self.__matriz = MatrizTPM(ruta)
        self.__emd = MetricasDistancia()
        self.__particiones_candidatas = []

    def estrategia1(self):
        self.__matriz.condiciones_de_background()
        self.__matriz.obtener_estado_nodo()
        self.__matriz.matriz_subsistema()
        self.__matriz.get_matriz_subsistema()
        t_inicio = time.time()
        self.encontrar_particion_menor()
        ic(self.__particiones_candidatas)
        ic(self.comparar_particiones())
        t_fin = time.time()
        t_proceso = t_fin - t_inicio
        ic(t_proceso)

    def encontrar_particion_menor(self):
        conjuntoV = self.__matriz.pasar_cadena_a_lista()
        ic(conjuntoV)
        self.algoritmo_principal(conjuntoV)

    def algoritmo_principal(self, V):
        if(len(V) == 1):
            return
        v1 = V[0]
        W = [v1]
        for i in range(len(V) - 1):
            mejor_iteracion = ()
            for j in list(set(V) - set(W)):
                subsistema = []
                u = []
                subsistema.extend(v1 if isinstance(v1[0], tuple) else [v1])
                subsistema.extend(j if isinstance(j[0], tuple) else [j])
                u.extend(j if isinstance(j[0], tuple) else [j])

                print("SE HACE LA V1 U U")
                ic(subsistema)
                resultadoEMD = self.realizar_emd(subsistema)

                print("SE HACE EL U")
                ic(u)
                resultadoEMD_nu= self.realizar_emd(u)

                resultado = resultadoEMD - resultadoEMD_nu
                ic(resultado)

                if mejor_iteracion == () or resultado < mejor_iteracion[0]:
                    mejor_iteracion = (resultado, j)
            
            W.append(mejor_iteracion[1])
        
        # Tomar los dos últimos elementos de W como el par candidato
        if len(W) >= 2:
            self.__particiones_candidatas.append((W[-1], W[:-1]))
            par_candidato = (W[-2], W[-1])
            # Quitar al arreglo v todos los elementos del par candidato
            V = list(set(V) - set(par_candidato))
            par_candidato_final = self.combinar_tuplas(par_candidato[0], par_candidato[1])
            V.append(par_candidato_final)

        self.algoritmo_principal(V)
    
    def realizar_emd(self, lista):
        matriz_normal, matriz_complemento = self.__matriz.marginalizar_normal_complemento(lista)
        est_n, est_c = self.__matriz.get_estado_inicial_n_c()
        self.__matriz.limpiar_estados_inicialies()
        resultado_tensorial = self.__matriz.producto_tensorial_matrices(matriz_normal[0], matriz_complemento[0], matriz_normal[1], matriz_complemento[1], est_n, est_c)
        resultados_lista = np.array(resultado_tensorial.iloc[0].values.tolist())
        return self.__emd.emd_pyphi(resultados_lista, self.__matriz.get_matriz_subsistema())

    def combinar_tuplas(self, t1, t2):
        # Verificar si t1 y t2 son tuplas de tuplas (tupla con otros elementos tipo tuple)
        es_tupla_de_tuplas_1 = all(isinstance(elem, tuple) for elem in t1)
        es_tupla_de_tuplas_2 = all(isinstance(elem, tuple) for elem in t2)

        # Agrupar `t1` y `t2` en una sola tupla de tuplas según su estructura
        if not es_tupla_de_tuplas_1:
            t1 = (t1,)  # Agrupa t1 en una sola tupla si no es una tupla de tuplas
        if not es_tupla_de_tuplas_2:
            t2 = (t2,)  # Agrupa t2 en una sola tupla si no es una tupla de tuplas

        # Combinar ambos resultados en una sola tupla
        return t1 + t2

    def comparar_particiones(self):
        particion_nueva = []
        particion = self.__particiones_candidatas[0]
        particion_nueva.extend(particion[0] if isinstance(particion[0][0], tuple) else [particion[0]])
        emd_inicial = self.realizar_emd(particion_nueva)
        particion_optima = (emd_inicial, particion)
        for i in range(1, len(self.__particiones_candidatas)):
            particion_nueva = []
            p = self.__particiones_candidatas[i]
            particion_nueva.extend(p[0] if isinstance(p[0][0], tuple) else [p[0]])
            emd_resultado = self.realizar_emd(particion_nueva)
            if emd_resultado < particion_optima[0]:
                particion_optima = (emd_resultado, p)

        return particion_optima
            