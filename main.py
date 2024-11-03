import numpy as np
import pandas as pd
from modelos.AlgoritmoPrincipal import AlgoritmoPrincipal
from modelos.LectorExcel import LectorExcel
from icecream import ic
from modelos.matriz import MatrizTPM
from numpy.typing import NDArray
from functools import reduce

def main():
    algoritmo = AlgoritmoPrincipal('archivos/matrizGuia.csv')
    # algoritmo2 = AlgoritmoPrincipal('archivos\matriz_6_variables.csv')
    algoritmo.estrategia1()

if __name__ == '__main__':
    main()