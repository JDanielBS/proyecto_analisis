import pandas as pd
import math

class MatrizTPM:
  def __init__(self, route):
    self.__matriz = pd.DataFrame = pd.read_csv(route, sep=',', header=None)
    self.indexar_matriz()

  def indexar_matriz(self):
    '''
     Indexa las filas y columnas de la matriz con etiquetas en formato little-endian
    '''
    filas = self.__matriz.shape[0]
    columnas = self.__matriz.shape[1]
    
    num_etiquetas = max(filas, columnas)
    num_bits = math.ceil(math.log2(num_etiquetas))  
    
    labels = list(self.lil_endian_int(num_bits, num_etiquetas))
    print("Etiquetas generadas en formato little-endian:", labels)
    
    if len(labels) >= columnas:
      self.__matriz.columns = labels[:columnas]
    if len(labels) >= filas:
      self.__matriz.index = labels[:filas]
    
    print("Matriz con etiquetas de columnas y filas indexadas:")
    print(self.__matriz)

  def lil_endian_int(self, n: int, num_etiquetas: int):
    '''
     Genera representaciones en formato little-endian de números binarios.
    '''
    for state in range(num_etiquetas):
      yield bin(state)[2:].zfill(n)[::-1]

  def eliminar_filas_por_bits(self, sistema_candidato, estado_inicial):
    """
    Elimina las filas cuyos índices tengan un bit específico en la posición indicada.
    """
    indices = self.obtener_indices_de_ceros(sistema_candidato)

    for i in indices:
      bit_indicado = estado_inicial[i]
      filas_a_mantener = [j for j in self.__matriz.index if j[i] == bit_indicado]
      print(filas_a_mantener, "filasmantener")
      self.__matriz = self.__matriz.loc[filas_a_mantener]
      filas_a_mantener.clear()

    nuevos_indices = [
        ''.join([fila[i] for i in range(len(fila)) if i not in indices])
        for fila in self.__matriz.index
    ]
    self.__matriz.index = nuevos_indices

  def obtener_indices_de_ceros(self, sistema_candidato):
    """
    Obtiene los índices de todas las apariciones de '0' en representación binaria.
    
    :param sistema_candidato: La representación binaria como cadena.
    :return: Una lista de índices donde se encuentran los '0's.
    """
    indices = []  
    
    for idx, bit in enumerate(sistema_candidato):
      if bit == '0':
        indices.append(idx) 
    return indices 

  def get_matriz(self):
    return print(self.__matriz)