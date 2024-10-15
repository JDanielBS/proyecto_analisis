import pandas as pd
import math

class MatrizTPM:
  def __init__(self, route):
    self.__matriz = pd.DataFrame = pd.read_csv(route, sep=',', header=None)
    self.indexar_matriz()

  def indexar_matriz(self):
    filas = self.__matriz.shape[0]
    columnas = self.__matriz.shape[1]
    
    # Calcular el número de etiquetas necesarias (número máximo entre filas y columnas)
    num_etiquetas = max(filas, columnas)
    
    # Determinar el número de bits necesarios para representar las etiquetas
    num_bits = math.ceil(math.log2(num_etiquetas))  # Usamos 'ceil' para asegurarnos de cubrir todas las etiquetas
    
    # Generar las etiquetas para las columnas y filas en formato little-endian
    labels = list(self.lil_endian_int(num_bits, num_etiquetas))
    print("Etiquetas generadas en formato little-endian:", labels)
    
    # Asignar las etiquetas a las columnas y filas si coinciden los tamaños
    if len(labels) >= columnas:
      self.__matriz.columns = labels[:columnas]
    if len(labels) >= filas:
      self.__matriz.index = labels[:filas]
    
    # Mostrar la matriz con las etiquetas indexadas
    print("Matriz con etiquetas de columnas y filas indexadas:")
    print(self.__matriz)

  def lil_endian_int(self, n: int, num_etiquetas: int):
    # Generar etiquetas en formato little-endian (binario invertido)
    for state in range(num_etiquetas):
      # Convertir el número a binario, agregar ceros a la izquierda y luego invertirlo (little-endian)
      yield bin(state)[2:].zfill(n)[::-1]

  def eliminar_filas_por_bits(self, sistema_candidato, estado_inicial):
    """
    Elimina las filas cuyos índices tengan un bit específico en la posición indicada (en little endian).
    
    :param bit_posicion: Posición del bit que quieres verificar (empezando en 0)
    :param valor_bit: Valor del bit que estás buscando ('0' o '1')
    """
    print(sistema_candidato)
    print(estado_inicial)
    indices = self.obtener_indices_de_ceros(sistema_candidato)
    indices_a_mantener = []

    for i in indices:
      bit_indicado = estado_inicial[i]
      indices_a_mantener.append([j for j in self.__matriz.index if j[i] != bit_indicado])
      self.__matriz = self.__matriz.loc[indices_a_mantener]
      indices_a_mantener = []

  def obtener_indices_de_ceros(self, sistema_candidato):
    """
    Obtiene los índices de todas las apariciones de '0' en la representación binaria.
    
    :param sistema_candidato: La representación binaria como cadena.
    :return: Una lista de índices donde se encuentran los '0's.
    """
    indices = []  # Lista para almacenar los índices de los '0's
    
    # Buscar todos los índices de '0'
    for idx, bit in enumerate(sistema_candidato):
      if bit == '0':
        indices.append(idx)  # Agregar el índice a la lista
    
    return indices  # Devolver la lista de índices

  def get_matriz(self):
    return print(self.__matriz)