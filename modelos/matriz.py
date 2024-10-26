import pandas as pd
import math
from modelos.sistema import Sistema


class MatrizTPM:
    def __init__(self, route):
        self.__matriz = pd.DataFrame = pd.read_csv(route, sep=",", header=None)
        self.__matriz_candidata = None
        self.__matriz_estado_nodo = []
        self.__listado_candidatos = []
        self.__listado_valores_futuros = []
        self.__listado_valores_presentes = []
        self.__sistema = Sistema("archivos/estructura.csv")

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
        print(self.__listado_candidatos, "listado candidatos")
        self.__listado_valores_futuros = self.obtener_indices(
            self.__sistema.get_subsistema_futuro(), "1"
        )
        print(self.__listado_valores_futuros, "listado valores futuros")
        self.__listado_valores_presentes = self.obtener_indices(
            self.__sistema.get_subsistema_presente(), "1"
        )
        print(self.__listado_valores_presentes, "listado valores presentes")
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

    def marginalizar(self, subsistema_presente, subsistema_futuro):
        self.marginalizar_filas(subsistema_presente)
        self.marginalizar_columnas(subsistema_futuro)

    def marginalizar_filas(self, subsistema_presente):
        """
        Marginaliza las filas de la matriz que no pertenecen al subsistema presente.
        """
        indices = self.obtener_indices(subsistema_presente, "0")

        nuevos_indices = [
            "".join([fila[i] for i in range(len(fila)) if i not in indices])
            for fila in self.__matriz_candidata.index
        ]
        self.__matriz_candidata.index = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        self.__matriz_candidata = self.__matriz_candidata.groupby(
            self.__matriz_candidata.index, sort=False
        ).mean()
        return self.__matriz_candidata
    
    def marginalizar_columnas(self, sistema_futuro):
        """
        Elimina las columnas cuyos índices tengan un bit específico en la posición indicada.
        """
        indices = self.obtener_indices(sistema_futuro, "0")

        nuevos_indices = [
            "".join([columna[i] for i in range(len(columna)) if i not in indices])
            for columna in self.__matriz_candidata.columns
        ]
        self.__matriz_candidata.columns = nuevos_indices

        # Transponemos la matriz para que las columnas se conviertan en filas, agrupamos, y luego volvemos a transponer
        self.__matriz_candidata = self.__matriz_candidata.T.groupby(self.__matriz_candidata.columns, sort=False).sum().T

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
  Marginalización por filas y columnas
  ------------------------------------------------------------------------------------------------
  """
    def obtener_estado_nodo():
        
        for i in range(len(self.__listado_candidatos)):
            self.marginalizar_columnas()
            self.__matriz_estado_nodo.append(self.__matriz_candidata)
            self.__matriz_candidata = self.__matriz.copy()