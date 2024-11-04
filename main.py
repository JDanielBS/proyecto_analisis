from modelos.AlgoritmoPrincipal import AlgoritmoPrincipal

def main():
    # algoritmo = AlgoritmoPrincipal('archivos/matrizGuia.csv')
    # algoritmo2 = AlgoritmoPrincipal('archivos\matriz_6_variables.csv')
    algoritmo3 = AlgoritmoPrincipal('archivos/resultado.csv')

    algoritmo3.estrategia1()

if __name__ == '__main__':
    main()