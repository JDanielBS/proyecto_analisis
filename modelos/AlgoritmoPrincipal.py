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
        conjuntoV = self.__matriz.pasar_cadena_a_lista()
        self.algoritmo_principal(conjuntoV)

    # TODO: verificar cuando es vacío en presente o en futuro
    def algoritmo_principal(self, V):
        if(len(V) == 2):
            return
        v1 = V[0]
        W = [v1]

        for i in range(len(V) - 1):
            for j in W:
                if j != v1:
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

                    presente = self.__matriz.pasar_lista_a_cadena(subsistema, '0')
                    futuro = self.__matriz.pasar_lista_a_cadena(subsistema, '1')
    