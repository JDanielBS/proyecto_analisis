import pandas as pd
import itertools
import math
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
        # Print detallado para depurar los valores de las listas
        print(f"Listado candidatos: {self.__listado_candidatos}")
        print(f"Listado valores futuros: {self.__listado_valores_futuros}")
        print(f"Listado valores presentes: {self.__listado_valores_presentes}")
    
    def get_valores_presentes(self):
        return self.__listado_valores_presentes
    
    def get_diccionario(self):
        return self.__matriz_estado_nodo_dict

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
        self.__estado_inicial_candidato = "".join([self.__sistema.get_estado_inicial()[i] for i in self.__listado_candidatos])
        print(self.__estado_inicial_candidato)
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
    def marginalizar(self, lista_subsistema, matriz, bit):
        bit_contrario = "0" if bit == "1" else "1"
        #  [(0, 0), (1, 1), (0, 1), (1, 3)]
        cadena_presente = self.pasar_lista_a_cadena(lista_subsistema, '0')
        cadena_futuro = self.pasar_lista_a_cadena(lista_subsistema,'1')
        indices_f = self.obtener_indices(cadena_futuro, bit_contrario)
        
        temporal = self.marginalizar_columnas("0" * len(self.__sistema.get_sistema_candidato()), self.__matriz_candidata.copy())  #el futuro es vacío                                                          
        indices_temporal = []
        for i in indices_f:
            key = self.__listado_candidatos[i]
            estado_nodo = self.__matriz_estado_nodo_dict[key]
            temporal = self.producto_tensorial_matrices(temporal, estado_nodo, indices_temporal, [key])
            indices_temporal.append(key)
        
        matriz_temp = self.marginalizar_filas(cadena_presente, temporal, bit)
        return matriz_temp

    def marginalizar_filas(self, subsistema_presente, matriz, bit):
        """
        Marginaliza las filas de la matriz que no pertenecen al subsistema presente.
        """
        # 0 para el normal, 1 para el complemento
        indices = self.obtener_indices(subsistema_presente, bit)

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
        print(sistema_futuro, 'sistema futuro en marginalizar')
        indices = self.obtener_indices(sistema_futuro, "0")
        print(indices, 'indices en marginalizar')
        
        print(matriz.columns, 'columnas en marginalizar')
        
        nuevos_indices = []

        # Recorre cada columna de la matriz
        for columna in matriz.columns:
            # Filtra los caracteres según los índices y únelos en una cadena
            indice_filtrado = "".join([columna[i] for i in range(len(columna)) if i not in indices])
            print(columna, 'columna en marginalizar')
            print(indice_filtrado, 'indice filtrado en marginalizar')
            nuevos_indices.append(indice_filtrado)

        print(nuevos_indices, 'nuevos indices en marginalizar')

        # nuevos_indices = [
        #     "".join([columna[i] for i in range(len(columna)) if i not in indices])
        #     for columna in matriz.columns
        # ]
        # print(nuevos_indices, 'nuevos indices en marginalizar')
        
         # Verificar y corregir cadenas vacías en nuevos_indices
        if all(indice == '' for indice in nuevos_indices):
            size = len(matriz.columns)
            nuevos_indices = ['0'] * (size // 2) + ['1'] * (size // 2)
        
        print(nuevos_indices, 'nuevos indices corregidos en marginalizar')
        
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
        print(cadena_dinamica, 'cadena dinamica')
        
        for i in range(len(sistema_candidato)):
            if i in self.__listado_candidatos:
                # Crear una cadena con un solo "1" en la posición correspondiente a la iteración actual
                subsistema_futuro = cadena_dinamica[:i] + "1" + cadena_dinamica[i+1:]
                print(subsistema_futuro, 'subsistema futuro')
                
                # Reiniciar matriz_estado_nodo a una copia de __matriz
                self.__matriz_estado_nodo = self.__matriz_candidata.copy()
                
                # Marginalizar columnas con el subsistema futuro
                matriz_estado = self.marginalizar_columnas(subsistema_futuro, self.__matriz_estado_nodo)
                print(matriz_estado, 'matriz estadooooooooos')

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
        resultado = pd.DataFrame(index=[self.__estado_inicial_candidato], columns=etiquetas_little_endian)

        # Obtener la fila del estado inicial candidato
        mat1 = mat1.loc[[self.__estado_inicial_candidato]]
        mat2 = mat2.loc[[self.__estado_inicial_candidato]]
        
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
            resultado.at[self.__estado_inicial_candidato, index_binario] = mat1.at[self.__estado_inicial_candidato, col1] * mat2.at[self.__estado_inicial_candidato, col2]
          

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
        cadena_dinamica = list("0" * len(self.__sistema.get_sistema_candidato()))
        print("Cadena dinámica inicial:", "".join(cadena_dinamica))
        
        # Recorre cada elemento de la lista
        for estado, posicion in lista:
            if estado == bit:
                # Coloca un "1" en la posición indicada
                cadena_dinamica[posicion] = "1"
        
        cadena_dinamica = "".join([cadena_dinamica[i] for i in self.__listado_candidatos])
        
        # Convierte la lista de caracteres de vuelta a una cadena
        return cadena_dinamica

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
        
        print(cadena_presente, "cadena presente")
        print(cadena_futuro, "cadena futuro")


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
        
        resultado2= self.producto_tensorial_matrices(matriz3, resultado, indices4, indices3)
        print(resultado2, 'ac*b')
        
    
    
    
    
