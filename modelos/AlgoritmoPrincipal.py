import time
from modelos.matriz import MatrizTPM
from icecream import ic
from modelos.MetricasDistancia import MetricasDistancia
import numpy as np
from itertools import chain


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
        particion_inicial = self.generar_particion_inicial()
        prueba= [(1,3)]
        self.estrategia_kmeans_logica(particion_inicial)
        ic(self.__particiones_candidatas)
        # self.encontrar_particion_menor()
        # ic(self.comparar_particiones())
        t_fin = time.time()
        t_proceso = t_fin - t_inicio
        ic(t_proceso)

    def encontrar_particion_menor(self):
        conjuntoV = self.__matriz.pasar_cadena_a_lista()
        # ic(conjuntoV)
        self.algoritmo_principal(conjuntoV)

    def algoritmo_principal(self, V):
        if(len(V) == 1):
            return
        W = [V[0]]
        for i in range(len(V) - 1):
            mejor_iteracion = ()
            for j in list(set(V) - set(W)):
                subsistema = list(chain.from_iterable((i,) if isinstance(i[0], int) else i for i in W))
                u = []
                subsistema.extend(j if isinstance(j[0], tuple) else [j])
                u.extend(j if isinstance(j[0], tuple) else [j])
                resultadoEMD = self.realizar_emd(subsistema)
                resultadoEMD_nu = self.realizar_emd(u)

                resultado = resultadoEMD[0] - resultadoEMD_nu[0]

                if mejor_iteracion == () or resultado < mejor_iteracion[0]:
                    mejor_iteracion = (resultado, j)

            W.append(mejor_iteracion[1])
        
        # Tomar los dos últimos elementos de W como el par candidato
        if len(W) >= 2:
            self.__particiones_candidatas.append([resultadoEMD[0], resultadoEMD[1], (W[-1], W[:-1])])
            par_candidato = (W[-2], W[-1])
            # Quitar al arreglo v todos los elementos del par candidato
            V = list(set(V) - set(par_candidato))
            par_candidato_final = self.combinar_tuplas(par_candidato[0], par_candidato[1])
            V.append(par_candidato_final)

        self.algoritmo_principal(V)
    
    def realizar_emd(self, lista):
        ic(lista)
        matriz_normal, matriz_complemento = self.__matriz.marginalizar_normal_complemento(lista)
        est_n, est_c = self.__matriz.get_estado_inicial_n_c()
        self.__matriz.limpiar_estados_inicialies()
        resultado_tensorial = self.__matriz.producto_tensorial_matrices(matriz_normal[0], matriz_complemento[0], matriz_normal[1], matriz_complemento[1], est_n, est_c)
        resultados_lista = np.array(resultado_tensorial.iloc[0].values.tolist(), dtype='float64')
        return (self.__emd.emd_pyphi(resultados_lista, self.__matriz.get_matriz_subsistema()), resultados_lista)

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
        particion_optima = []
        menor = self.__particiones_candidatas[0][0]

        # Buscar el menor EMD
        for i in self.__particiones_candidatas:
            if i[0] < menor:
                menor = i[0]

        # Agregar las particiones con el menor EMD a la lista de particiones óptimas
        for i in self.__particiones_candidatas:
            if i[0] == menor:
                particion_optima.append(i)

        with open('archivos/particion_optima.txt', 'w') as f:
            for i in particion_optima:
                arreglo = i[1]
                np.savetxt(f, arreglo, delimiter=',', fmt='%.5f')
                f.write('\n')  # Agregar una línea en blanco entre arreglos 
        
        return particion_optima
    
    def guardar_en_archivo(self, contenido, ruta):
        with open(ruta, "w") as archivo:
            archivo.write(str(contenido))  # Escribir el contenido como texto
            
    def generar_particion_inicial(self):
        nodos = self.__matriz.pasar_cadena_a_lista()
        
        particion1 = []
        particion2 = []

        # Asignar nodos a los subconjuntos de manera alternada
        for i, nodo in enumerate(nodos):
            if i % 2 == 0:
                particion1.append(nodo)
            else:
                particion2.append(nodo)

        return particion1
    def estrategia_kmeans_logica(self, particion_inicial):
            ic(particion_inicial)
            resultado = self.realizar_emd(particion_inicial)
            mejor_emd = resultado[0]
            distribucion = resultado[1]
            ic(distribucion)
            ic(mejor_emd)
            particion_complemento = self.__matriz.encontrar_complemento_particion(particion_inicial)
            mejor_particion = (particion_inicial, particion_complemento)
            print(mejor_particion, 'al iniciar')
            # # Probar moviendo nodos de particion1 a particion2
            for nodo in particion_inicial:
                nueva_particion1 = [n for n in particion_inicial if n != nodo]
                nueva_particion2 = particion_complemento + [nodo]
                resultado = self.realizar_emd(nueva_particion1)
                nuevo_emd = resultado[0]
                nueva_distribucion = resultado[1]
                ic(nueva_distribucion)
                ic(nuevo_emd)
                if nuevo_emd < mejor_emd:
                    mejor_emd = nuevo_emd
                    mejor_particion = (nueva_particion1, nueva_particion2)
                    distribucion = nueva_distribucion
            print(mejor_particion, 'al finalizar primer for')

            # # Probar moviendo nodos de particion2 a particion1
            for nodo in particion_complemento:
                nueva_particion2 = [n for n in particion_complemento if n != nodo]
                nueva_particion1 = particion_inicial + [nodo]
                resultado = self.realizar_emd(nueva_particion1)
                nuevo_emd = resultado[0]
                nueva_distribucion = resultado[1]
                ic(nueva_distribucion)              
                ic(nuevo_emd)
                
                if nuevo_emd < mejor_emd:
                    mejor_emd = nuevo_emd
                    mejor_particion = (nueva_particion1, nueva_particion2)
                    distribucion = nueva_distribucion   
            print(mejor_particion, 'al finalizar segundo for')
            
            diccionario_particiones = {
                'emd': mejor_emd,
                'particion1': mejor_particion[0],
                'particion2': mejor_particion[1],
                'distribucion_teorica': self.__matriz.get_matriz_subsistema(),
                'distribucion_experimental': distribucion
            }   
            ic(diccionario_particiones) 
            self.__particiones_candidatas.append(diccionario_particiones)
            
            # Llamada recursiva si se encontró una mejor partición
            if mejor_particion != (particion_inicial, particion_complemento):
                return self.estrategia_kmeans_logica(mejor_particion[0])
            
            return self.__particiones_candidatas
    
