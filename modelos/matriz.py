import pandas as pd
import itertools
import math
from icecream import ic
from modelos.sistema import Sistema


class MatrizTPM:
    def __init__(self, route):
        self.__matriz = pd.read_csv(route, sep=",", header=None)
        self.__matriz_candidata = None
        self.__matriz_subsistema = None
        self.__matriz_estado_nodo_dict = {}
        self.__matriz_estado_nodo_marginalizadas = {}
        self.__listado_candidatos = []
        self.__listado_valores_futuros = []
        self.__listado_valores_presentes = []
        self.__sistema = Sistema("archivos/estructura.csv")
        self.__estado_inicial_subsistema= None
        self.indexar_matriz()

    def get_matriz(self):
        return print(self.__matriz)
    
    def get_matriz_subsistema(self):
        return print(self.__matriz_subsistema)
      
    def get_listados(self):
        # Print detallado para depurar los valores de las listas
        print(f"Listado candidatos: {self.__listado_candidatos}")
        print(f"Listado valores futuros: {self.__listado_valores_futuros}")
        print(f"Listado valores presentes: {self.__listado_valores_presentes}")
    
    def get_valores_presentes(self):
        return self.__listado_valores_presentes
    
    def get_diccionario(self):
        return self.__matriz_estado_nodo_dict
    
    def get_dic_marginalizadas(self):
        return self.__matriz_estado_nodo_marginalizadas

    """
    ------------------------------------------------------------------------------------------------
    Poner en notación little endian
    ------------------------------------------------------------------------------------------------
    """

    def indexar_matriz(self):
        """
        Indexa las filas y columnas de la matriz con etiquetas en formato little-endian
        """
        filas = self.__matriz.shape[0]
        columnas = self.__matriz.shape[1]

        num_etiquetas = max(filas, columnas)
        num_bits = math.ceil(math.log2(num_etiquetas))

        labels = list(self.lil_endian_int(num_bits, num_etiquetas))

        if len(labels) >= columnas:
            self.__matriz.columns = labels[:columnas]
        if len(labels) >= filas:
            self.__matriz.index = labels[:filas]

    def lil_endian_int(self, n: int, num_etiquetas: int):
        """
        Genera representaciones en formato little-endian de números binarios.
        """
        for state in range(num_etiquetas):
            yield bin(state)[2:].zfill(n)[::-1]

    """
    ------------------------------------------------------------------------------------------------
    Condiciones de background
    ------------------------------------------------------------------------------------------------
    """
    def condiciones_de_background(self):
        """
        Elimina las filas y columnas de la matriz que no cumplen con las condiciones de background.
        """
        self.__listado_candidatos = self.obtener_indices(self.__sistema.get_sistema_candidato(), "1")
        self.__listado_valores_futuros = self.obtener_indices(
            self.__sistema.get_subsistema_futuro(), "1")
        self.__listado_valores_presentes = self.obtener_indices(
            self.__sistema.get_subsistema_presente(), "1")        # a partir de los indices de listado candidatos, se obtiene el estado inicial candidato
        self.__estado_inicial_subsistema = "".join([self.__sistema.get_estado_inicial()[i] for i in self.__listado_valores_presentes])
        self.eliminar_filas_por_bits(self.__sistema.get_sistema_candidato(), self.__sistema.get_estado_inicial())
        self.eliminar_columnas_por_bits(self.__sistema.get_sistema_candidato())
        self.__matriz_candidata = self.__matriz.copy()

    def eliminar_filas_por_bits(self, sistema_candidato, estado_inicial):
        """
        Elimina las filas cuyos índices tengan un bit específico en la posición indicada.
        """
        indices = self.obtener_indices(sistema_candidato, "0")

        for i in indices:
            bit_indicado = estado_inicial[i]
            filas_a_mantener = [j for j in self.__matriz.index if j[i] == bit_indicado]
            self.__matriz = self.__matriz.loc[filas_a_mantener]
            filas_a_mantener.clear()

        nuevos_indices = [
            "".join([fila[i] for i in range(len(fila)) if i not in indices])
            for fila in self.__matriz.index
        ]
        self.__matriz.index = nuevos_indices

    def eliminar_columnas_por_bits(self, sistema_candidato):
        """
        Elimina las columnas cuyos índices tengan un bit específico en la posición indicada.
        """
        indices = self.obtener_indices(sistema_candidato, "0")

        nuevos_indices = [
            "".join([columna[i] for i in range(len(columna)) if i not in indices])
            for columna in self.__matriz.columns
        ]
        self.__matriz.columns = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        self.__matriz = self.__matriz.T.groupby(self.__matriz.columns, sort=False).sum().T

    def obtener_indices(self, sistema_candidato, num_indicado):
        """
        Obtiene los índices de todas las apariciones del numero indicado en representación binaria.
        """
        indices = []

        for idx, bit in enumerate(sistema_candidato):
            if bit == num_indicado:
                indices.append(idx)
        return indices
    
    def matriz_subsistema(self):
        # [(0,0), (1,0), (1,1), (1,2)]
        # leer el subsistema presente y futuro
        indices_f= self.obtener_indices(self.__sistema.get_subsistema_futuro(), '1') # 0, 1, 2
        # obtener el estado_nodo del diccionario de acuerdo a los indices_f

        temporal = self.marginalizar_columnas('0'*len(self.__listado_candidatos), self.__matriz_candidata.copy(), '1') # 000, matriz de unos
        temporal_marginalizada = self.marginalizar_filas(self.__sistema.get_subsistema_presente(), temporal, '1')
        indices_temporal = []
        for i in indices_f:
            matriz_futuro = self.__matriz_estado_nodo_dict[i].copy()
            matriz_marginalizada = self.marginalizar_filas(self.__sistema.get_subsistema_presente(), matriz_futuro, '1')
            self.__matriz_estado_nodo_marginalizadas[i] = matriz_marginalizada
            temporal_marginalizada = self.producto_tensorial_matrices(temporal_marginalizada, matriz_marginalizada, indices_temporal, [i])
            indices_temporal.append(i)
            
        self.__matriz_subsistema = temporal_marginalizada.values

    # def obtener_vector_subsitema_teorico(self):
    #     '''
    #     Marginaliza las filas y columnas de la matriz que no pertenecen al subsistema presente y futuro.
    #     Bit en 1 si se quiere hacer de manera normal, 0 si se quiere el complemento.
    #     '''
    #     subsistema_futuro = self.__sistema.get_subsistema_futuro()
    #     subsistema_presente = self.__sistema.get_subsistema_presente()
    #     temporal = self.marginalizar_columnas(subsistema_futuro, self.__matriz_candidata.copy(), '1')
    #     matriz_temp = self.marginalizar_filas(subsistema_presente, temporal, '1')
    #     matriz_temp = matriz_temp.loc[[self.__estado_inicial_subsistema]]
    #     self.__matriz_subsistema = matriz_temp

    """
    ------------------------------------------------------------------------------------------------
    Marginalización por filas y columnas
    ------------------------------------------------------------------------------------------------
    """
    def marginalizar_normal_complemento(self, lista_subsistema):
        # sistema candidato = abd
        # [(0,0), (1,0), (1,1), (1,3)]
        # [(0,0), (1,1), (1,3)]
        cadena_presente = self.pasar_lista_a_cadena(lista_subsistema, 0)
        cadena_futuro = self.pasar_lista_a_cadena(lista_subsistema, 1)

        normal = self.marginalizar_bits(cadena_presente, cadena_futuro, '1')
        complemento = self.marginalizar_bits(cadena_presente, cadena_futuro, '0')

        indices_n = self.obtener_indices(cadena_futuro, '1')
        indices_c = self.obtener_indices(cadena_futuro, '0')

        i = 0
        j = 0
        while i < len(indices_n) and j < len(indices_c):
            if indices_n[i] < indices_c[j]:
                indices_n[i] = self.__listado_valores_futuros[indices_n[i]]
                i += 1
            else:
                indices_c[i] = self.__listado_valores_futuros[indices_c[i]]
                j += 1
        while i < len(indices_n):
            indices_n[i] = self.__listado_valores_futuros[indices_n[i]]
            i += 1
        while j < len(indices_c):
            indices_c[j] = self.__listado_valores_futuros[indices_c[j]]
            j += 1
        
        return (normal, indices_n), (complemento, indices_c)

    def marginalizar_bits(self, cadena_presente, cadena_futuro, bit):
        '''
        Marginaliza las filas y columnas de la matriz que no pertenecen al subsistema presente y futuro.
        Bit en 1 si se quiere hacer de manera normal, 0 si se quiere el complemento.
        '''
        indices_futuros = self.obtener_indices(cadena_futuro, bit) #BC
        if len(indices_futuros) == 1:
            key = self.__listado_valores_futuros[indices_futuros[0]]
            temporal = self.__matriz_estado_nodo_marginalizadas[key].copy() #0
            temporal_marginalizada = self.marginalizar_filas(cadena_presente, temporal, bit)
        else:
            temporal = self.marginalizar_columnas('0'*len(self.__listado_candidatos), self.__matriz_candidata.copy(), '1') # 000, matriz de unos
            temporal_marginalizada = self.marginalizar_filas(cadena_presente, temporal, '1')
            indices_temporal = []
            for i in indices_futuros:
                key = self.__listado_valores_futuros[i]
                matriz_futuro = self.__matriz_estado_nodo_marginalizadas[key].copy()
                matriz_marginalizada = self.marginalizar_filas(cadena_presente, matriz_futuro, bit)
                temporal_marginalizada = self.producto_tensorial_matrices(temporal_marginalizada, matriz_marginalizada, indices_temporal, [i])
                indices_temporal.append(i)

        return temporal_marginalizada

    def marginalizar_filas(self, subsistema_presente, matriz, bit):
        """
        Marginaliza las filas de la matriz que no pertenecen al subsistema presente.
        """
        # 1 para el normal, 0 para el complemento
        indices = self.obtener_indices(subsistema_presente, bit)
        nuevos_indices = []

        # Recorre cada fila de la matriz
        if(indices != []):
            nuevos_indices = [
                "".join([fila[i] for i in range(len(fila)) if i in indices]) or fila[-1]
                for fila in matriz.index
            ]
        else:
            for _ in range(len(matriz.index)):
                nuevos_indices.append('')
        
        matriz.index = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        matriz = matriz.groupby(matriz.index, sort=False).mean()
        return matriz
      
    def marginalizar_columnas(self, sistema_futuro, matriz, bit):
        """
        Elimina las columnas cuyos índices tengan un bit específico en la posición indicada.
        """
        indices = self.obtener_indices(sistema_futuro, bit)
        
        nuevos_indices = []

        # Recorre cada columna de la matriz
        if(indices != []):
            nuevos_indices = [
                "".join([columna[i] for i in range(len(columna)) if i in indices]) or columna[-1]
                for columna in matriz.columns
            ]
        else:
            for _ in range(len(matriz.columns)):
                nuevos_indices.append('')
        
        matriz.columns = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        matriz = matriz.T.groupby(matriz.columns, sort=False).sum().T
        return matriz
        
    """
    ------------------------------------------------------------------------------------------------
    Obtener estado nodo
    ------------------------------------------------------------------------------------------------
    """
    def obtener_estado_nodo(self):
        sistema_candidato = self.__sistema.get_sistema_candidato()
        cadena_dinamica = "0" * len(sistema_candidato)
        
        for i in range(len(sistema_candidato)):
            if i in self.__listado_candidatos:
                # Crear una cadena con un solo "1" en la posición correspondiente a la iteración actual
                subsistema_futuro = cadena_dinamica[:i] + "1" + cadena_dinamica[i+1:]
                
                # Reiniciar matriz_estado_nodo a una copia de __matriz
                self.__matriz_estado_nodo = self.__matriz_candidata.copy()
                
                # Marginalizar columnas con el subsistema futuro
                matriz_estado = self.marginalizar_columnas(subsistema_futuro, self.__matriz_estado_nodo, '1')

                # Guardar la matriz de estado nodo en un diccionario con el índice como clave
                self.__matriz_estado_nodo_dict[i] = matriz_estado
    
    
    def producto_tensorial_matrices(self, mat1, mat2, indices1, indices2):
        # Crear etiquetas en formato little-endian para las combinaciones de columnas
        n_cols_resultado = 2 ** (len(indices1) + len(indices2))
        etiquetas_little_endian = [
            "".join(str((i >> k) & 1) for k in range(len(indices1) + len(indices2)))
            for i in range(n_cols_resultado)
        ]

        # Crear la matriz de resultado con las nuevas etiquetas de columnas
        resultado = pd.DataFrame(index=[self.__estado_inicial_subsistema], columns=etiquetas_little_endian)

        # Obtener la fila del estado inicial candidato
        if len(mat1) == 1 and mat1.index[0] == '':
            fila_inicial_m1 = ''
        else:
            fila_inicial_m1 = self.__estado_inicial_subsistema
        if len(mat2) == 1 and mat2.index[0] == '':
            fila_inicial_m2 = ''
        else:
            fila_inicial_m2 = self.__estado_inicial_subsistema
        
        mat1 = mat1.loc[[fila_inicial_m1]]
        mat2 = mat2.loc[[fila_inicial_m2]]
        
        # Iterar sobre cada combinación de columnas para realizar el producto tensorial
        for col1, col2 in itertools.product(mat1.columns, mat2.columns):
            # Construir el índice binario en formato little-endian de manera directa
            index_binario = ""
            i, j, k = 0, 0, 0

            # Iterar a través de los arreglos
            while i < len(indices1) and j < len(indices2):
                if indices1[i] < indices2[j]:
                    index_binario += str(col1)[i]
                    i += 1
                else:
                    index_binario += str(col2)[j]
                    j += 1
                k += 1

            # Una vez que uno de los arreglos ha sido completado,
            # ponemos los bits restantes
            while i < len(indices1):
                index_binario += str(col1)[i]
                i += 1
                k += 1
            while j < len(indices2):
                index_binario += str(col2)[j]
                j += 1
                k += 1

            # Calcular y asignar el producto
            # Calcular y asignar el producto en la fila correspondiente
            resultado.at[self.__estado_inicial_subsistema, index_binario] = mat1.at[fila_inicial_m1, col1] * mat2.at[fila_inicial_m2, col2]

        # Llenar valores NaN con 0 para la matriz de salida
        resultado.fillna(0, inplace=True)
        
        return resultado

    """
    ------------------------------------------------------------------------------------------------
    Carpintería
    ------------------------------------------------------------------------------------------------
    """
    def pasar_lista_a_cadena(self, lista, bit):
        """
        Convierte una lista de enteros en una cadena de bits.
        """
        # Inicializa la cadena con ceros y la convierte en una lista mutable
        # [(0,0), (1,3)]
        if bit == 0:
            longitud = len(self.__listado_valores_presentes)
        else:
            longitud = len(self.__listado_valores_futuros)

        cadena_dinamica = list("0" * longitud)
        
        # Recorre cada elemento de la lista 
        for estado, posicion in lista:
            if estado == bit:
                # Coloca un "1" en la posición indicada
                index = self.__listado_valores_presentes.index(posicion) if bit == 0 else self.__listado_valores_futuros.index(posicion)
                cadena_dinamica[index] = "1"
        
        if bit == 0:
            cadena_dinamica = "".join([cadena_dinamica[i] for i in range(len(self.__listado_valores_presentes))])
        else:
            cadena_dinamica = "".join([cadena_dinamica[i] for i in range(len(self.__listado_valores_futuros))])
        
        # Convierte la lista de caracteres de vuelta a una cadena
        return cadena_dinamica
    
    def pasar_cadena_a_lista(self):
        """
        Convierte una cadena de bits a una lista.
        """
        indices_f = self.obtener_indices(self.__sistema.get_subsistema_futuro(), "1")
        indices_p = self.obtener_indices(self.__sistema.get_subsistema_presente(), "1")
        listado = []

        for i in indices_p:
            listado.append((0, i))
        for i in indices_f:
            listado.append((1, i))

        return listado

    def prueba_lista(self):
        # Verificar que no ingrese variables que no estén en el sistema candidato
        # 1101 ABD A, B, D = 0, 1, 3
        lista = [(0, 0), (1, 1), (0, 1), (1, 3)]
        # BD|ab
        # 0101 cadena futuro 011
        # 1100 cadena presente 110
        #0101 cadena futuro 011=  100 
        
        cadena_presente = self.pasar_lista_a_cadena(lista, 0)
        cadena_futuro = self.pasar_lista_a_cadena(lista, 1)
        
        
    def prueba_producto_tensorial(self):
        #mandamos del diccionario self.__matriz_estado_nodo_dict el indice 0 y 2
   
        matriz1 = self.__matriz_estado_nodo_dict[0]
        matriz2 = self.__matriz_estado_nodo_dict[1]
        indices1 = [0]
        indices2 = [1]
        
        indices3= [0, 1]
        indices4= [2]
        
        matriz3 = self.__matriz_estado_nodo_dict[2]
        
        matriz1 = self.marginalizar_filas(self.__sistema.get_subsistema_presente(), matriz1, '1')
        matriz2 = self.marginalizar_filas(self.__sistema.get_subsistema_presente(), matriz2, '1')
        matriz3 = self.marginalizar_filas(self.__sistema.get_subsistema_presente(), matriz3, '1')

        resultado = self.producto_tensorial_matrices(matriz1, matriz2, indices1, indices2)
        print(resultado, 'ab')
        
        resultado2= self.producto_tensorial_matrices(matriz3, resultado, indices4, indices3)
        print(resultado2, 'abc')

        print("Resultado final", resultado2)
    
    def prueba_marginalizar(self):
        #mandamos del diccionario self.__matriz_estado_nodo_dict el indice 0 y 2
        # lista = [(0, 0), (1, 1), (0, 1), (1, 3)]
        ic(self.get_dic_marginalizadas())
        lista = [(0, 0), (1, 0)]
        
        # A|a normal
        normal, complemento = self.marginalizar_normal_complemento(lista)
        ic(normal)
        ic(complemento)
    
