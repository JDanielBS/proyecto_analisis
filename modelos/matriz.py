import pandas as pd
import itertools
import math
import os
import csv
from modelos.sistema import Sistema


class MatrizTPM:
    def __init__(self, route):
        self.__matriz = pd.read_csv(route, sep=",", header=None)
        self.__matriz_candidata = None
        self.__matriz_estado_nodo_dict = {}
        self.__listado_candidatos = []
        self.__listado_valores_futuros = []
        self.__listado_valores_presentes = []
        self.__sistema = Sistema("archivos/estructura.csv")
        self.__estado_inicial_candidato= None

        self.indexar_matriz()

    def get_matriz(self):
        return print(self.__matriz)
      
    def get_listados(self):
        return self.__listado_candidatos, self.__listado_valores_futuros, self.__listado_valores_presentes

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
    def condiciones_de_background(self, sistema_candidato, estado_inicial):
        """
        Elimina las filas y columnas de la matriz que no cumplen con las condiciones de background.
        """
        self.__listado_candidatos = self.obtener_indices(sistema_candidato, "1")
        self.__listado_valores_futuros = self.obtener_indices(
            self.__sistema.get_subsistema_futuro(), "1")
        self.__listado_valores_presentes = self.obtener_indices(
            self.__sistema.get_subsistema_presente(), "1")
        # a partir de los indices de listado candidatos, se obtiene el estado inicial candidato
        self.__estado_inicial_candidato = "".join([estado_inicial[i] for i in self.__listado_candidatos])
        print(self.__estado_inicial_candidato)
        self.eliminar_filas_por_bits(sistema_candidato, estado_inicial)
        self.eliminar_columnas_por_bits(sistema_candidato)
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
        self.__listado_valores_presentes = []

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
        Obtiene los índices de todas las apariciones de '0' en representación binaria.
        """
        indices = []

        for idx, bit in enumerate(sistema_candidato):
            if bit == num_indicado:
                indices.append(idx)
        return indices

    """
    ------------------------------------------------------------------------------------------------
    Marginalización por filas y columnas
    ------------------------------------------------------------------------------------------------
    """
    def marginalizar_subsistema_entrada(self, subsistema_presente, subsistema_futuro):
      matriz_temp = self.__matriz_candidata.copy()
      matriz_temp= self.marginalizar(subsistema_presente, subsistema_futuro, matriz_temp)
      self.__matriz_candidata = matriz_temp

    def marginalizar(self, subsistema_presente, subsistema_futuro, matriz):
       matriz_temp = matriz.copy()
       matriz_temp = self.marginalizar_filas(subsistema_presente, matriz_temp)
       matriz_temp = self.marginalizar_columnas(subsistema_futuro, matriz_temp)
       matriz= matriz_temp
       return matriz

    def marginalizar_filas(self, subsistema_presente, matriz):
        """
        Marginaliza las filas de la matriz que no pertenecen al subsistema presente.
        """
        indices = self.obtener_indices(subsistema_presente, "0")

        nuevos_indices = [
            "".join([fila[i] for i in range(len(fila)) if i not in indices])
            for fila in matriz.index
        ]
        
        matriz.index = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        matriz = matriz.groupby(matriz.index, sort=False).mean()
        return matriz
      
    def marginalizar_columnas(self, sistema_futuro, matriz):
        """
        Elimina las columnas cuyos índices tengan un bit específico en la posición indicada.
        """
        indices = self.obtener_indices(sistema_futuro, "0")

        nuevos_indices = [
            "".join([columna[i] for i in range(len(columna)) if i not in indices])
            for columna in matriz.columns
        ]
        matriz.columns = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        matriz = matriz.T.groupby(matriz.columns, sort=False).sum().T
        return matriz

    def calcular_complemento(self, subsistema_futuro, subsistema_presente):
        """
        Calcula la matriz complemento tomando en cuenta el subsistema futuro y presente
        """
        matriz_complemento = self.__matriz.copy()
        indices_f = self.obtener_indices(subsistema_futuro, "1")
        indices_p = self.obtener_indices(subsistema_presente, "1")

        nuevos_indices = [
            "".join([columna[i] for i in range(len(columna)) if i not in indices])
            for columna in self.__matriz_candidata.columns
        ]
        self.__matriz_candidata.columns = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        self.__matriz_candidata = (
            self.__matriz_candidata.T.groupby(
                self.__matriz_candidata.columns, sort=False
            )
            .sum()
            .T
        )
        return matriz_complemento
        
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
                self.__matriz_estado_nodo = self.__matriz.copy()
                
                # Marginalizar columnas con el subsistema futuro
                matriz_estado = self.marginalizar_columnas(subsistema_futuro, self.__matriz_estado_nodo)

                # Guardar la matriz de estado nodo en un diccionario con el índice como clave
                self.__matriz_estado_nodo_dict[i] = matriz_estado
    
    # def producto_tensorial_matrices(self, mat1, mat2, indices1, indices2):
    #     # Crear una lista de combinaciones de columnas en little-endian para los índices seleccionados
    #     n_cols_resultado = 2 ** (len(indices1) + len(indices2))
    #     etiquetas_little_endian = [
    #         "".join(str((i >> k) & 1) for k in range(len(indices1) + len(indices2)))
    #         for i in range(n_cols_resultado)
    #     ]

    #     # Inicializar matriz resultado con nuevas columnas en formato little-endian
    #     resultado = pd.DataFrame(index=mat1.index, columns=etiquetas_little_endian)

    #     # Iterar sobre todas las combinaciones de posiciones en las columnas seleccionadas de ambas matrices
    #     for col1, col2 in itertools.product(mat1.columns, mat2.columns):
    #         # Obtener el índice de la combinación en formato little-endian
    #         index_binario = ""
            
    #         # Llenar la combinación bit a bit con los bits en el orden little-endian
    #         for i, bit in enumerate(indices1 + indices2):
    #             if bit < len(indices1):
    #                 index_binario += col1[bit]
    #             else:
    #                 index_binario += col2[bit - len(indices1)]

    #         # Asignar el producto en la posición correspondiente
    #         resultado[index_binario] = mat1[col1] * mat2[col2]

    #     # Reemplazar NaN con 0 para valores sin combinación
    #     resultado.fillna(0, inplace=True)
        
    #     return resultado
    
    # def producto_tensorial_matrices(self, mat1, mat2, indices1, indices2):
    #     # Comprobar que ambas matrices tienen el mismo número de filas
    #     if len(mat1) != len(mat2):
    #         raise ValueError("Ambas matrices deben tener el mismo número de filas.")
        
    #     # Crear etiquetas en formato little-endian para las combinaciones de columnas
    #     n_cols_resultado = 2 ** (len(indices1) + len(indices2))
    #     etiquetas_little_endian = [
    #         "".join(str((i >> k) & 1) for k in range(len(indices1) + len(indices2)))
    #         for i in range(n_cols_resultado)
    #     ]

    #     # Crear la matriz de resultado con las nuevas etiquetas de columnas
    #     resultado = pd.DataFrame(index=mat1.index, columns=etiquetas_little_endian)

    #     # Iterar sobre cada fila para realizar el producto tensorial fila por fila
    #     for row in mat1.index:
    #         for col1, col2 in itertools.product(mat1.columns, mat2.columns):
    #             # Construir el índice binario en formato little-endian
    #             index_binario = ""
    #             for i, bit in enumerate(indices1 + indices2):
    #                 if bit < len(indices1):
    #                     index_binario += str(col1)[bit]
    #                 else:
    #                     index_binario += str(col2)[bit - len(indices1)]
                
    #             # Calcular y asignar el producto
    #             resultado.loc[row, index_binario] = mat1.loc[row, col1] * mat2.loc[row, col2]

    #     # Llenar valores NaN con 0 para la matriz de salida
    #     resultado.fillna(0, inplace=True)
    
    
    def producto_tensorial_matrices(self, mat1, mat2, indices1, indices2):
        print(mat1, 'miremosss')
        print(mat2, 'miremosss 2')
        print('indices', indices1, indices2)
        
        # Crear etiquetas en formato little-endian para las combinaciones de columnas
        n_cols_resultado = 2 ** (len(indices1) + len(indices2))
        etiquetas_little_endian = [
            "".join(str((i >> k) & 1) for k in range(len(indices1) + len(indices2)))
            for i in range(n_cols_resultado)
        ]
        
        print(etiquetas_little_endian, 'etiquetas_little_endian')

        # Crear la matriz de resultado con las nuevas etiquetas de columnas
        resultado = pd.DataFrame(index=[self.__estado_inicial_candidato], columns=etiquetas_little_endian)

        # Obtener la fila del estado inicial candidato
        mat1 = mat1.loc[[self.__estado_inicial_candidato]]
        mat2 = mat2.loc[[self.__estado_inicial_candidato]]
        print(mat1, 'row_initial_candidate mt1')

         # Iterar sobre cada combinación de columnas para realizar el producto tensorial
        for col1, col2 in itertools.product(mat1.columns, mat2.columns):
            # Construir el índice binario en formato little-endian de manera directa
            index_binario = f"{col1}{col2}"  # Combinar las etiquetas de columnas directamente
            
            # Calcular y asignar el producto
              # Calcular y asignar el producto en la fila correspondiente
            resultado.at[self.__estado_inicial_candidato, index_binario] = mat1.at[self.__estado_inicial_candidato, col1] * mat2.at[self.__estado_inicial_candidato, col2]
          

        # Llenar valores NaN con 0 para la matriz de salida
        resultado.fillna(0, inplace=True)
        
        return resultado

            
    def prueba_producto_tensorial(self):
   #mandamos del diccionario self.__matriz_estado_nodo_dict el indice 0 y 2
   
        matriz1 = self.__matriz_estado_nodo_dict[0]
        matriz2 = self.__matriz_estado_nodo_dict[2]
        indices1 = [0]
        indices2 = [2]
        
        indices3= [0, 2]
        indices4= [1]
        
        matriz3 = self.__matriz_estado_nodo_dict[1]
        
        resultado = self.producto_tensorial_matrices(matriz1, matriz2, indices1, indices2)
        print(resultado, 'ac')
        
        resultado2= self.producto_tensorial_matrices(resultado, matriz3, indices3, indices4)
        print(resultado2, 'ac*b')
    
    
    
#     B * AC
#    ! A * C
    