from modelos.AlgoritmoPrincipal import AlgoritmoPrincipal
from modelos.AlgoritmoFuerzaBruta import AlgoritmoFuerzaBruta
 
def main():
    # algoritmo1 = AlgoritmoPrincipal('archivos/resultado.csv')
    algoritmo2 = AlgoritmoFuerzaBruta('archivos/resultado.csv')
    # algoritmo1.estrategia1()
    algoritmo2.estrategia_fuerza_bruta()

if __name__ == '__main__':
    main()