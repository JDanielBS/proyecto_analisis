import csv

class Sistema:

    def __init__(self):
        self.__variables
        self.__estado_inicial
        self.__background
        self.__subsistema
        self.__estado_subsistema

    def set_with_route(self, route):
        with open('matriz_probabilidad.csv', mode='r') as archivo:
            lector = csv.reader(archivo)
            matriz_probabilidad = [list(map(float, fila)) for fila in lector]

    def get_variables(self):
        return self.__variables
    
    def get_estado_inicial(self):
        return self.__estado_inicial
    
    def get_sistema_candidato(self):
        return self.__background
    
    def get_subsistema(self):
        return self.__subsistema
    
    def set_variables(self, variables):
        self.__variables = variables

    def set_estado_inicial(self, estado_inicial):
        self.__estado_inicial = estado_inicial

    def set_sistema_candidato(self, background):
        self.__background = background
    
    def set_subsistema(self, subsistema):
        self.__subsistema = subsistema
