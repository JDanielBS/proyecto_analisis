import csv
import json

class Sistema:

    def __init__(self):
        self.__variables
        self.__estado_inicial
        self.__background
        self.__subsistema
        self.__estado_subsistema

    def set_with_csv(self, ruta):
        with open(ruta, mode='r') as archivo:
            lector = csv.reader(archivo)
            fila = next(lector)
            if len(fila) >= 6:
                self.__variables = fila[0].strip()
                self.__estado_inicial = fila[1].strip()
                self.__background = fila[2].strip()
                self.__subsistema = fila[3].strip()
                self.__estado_subsistema = fila[4].strip()
            else:
                raise ValueError("El archivo CSV no tiene suficientes columnas")
            
    def set_with_json(self, ruta):
        with open(ruta, mode='r') as archivo:
            contenido = json.load(archivo)
            self.__variables = contenido["variables"]
            self.__estado_inicial = contenido["estado_inicial"]
            self.__background = contenido["background"]
            self.__subsistema = contenido["subsistema"]
            self.__estado_subsistema = contenido["estado_subsistema"]

    def get_variables(self):
        return self.__variables
    
    def get_estado_inicial(self):
        return self.__estado_inicial
    
    def get_sistema_candidato(self):
        return self.__background
    
    def get_subsistema(self):
        return self.__subsistema
    
    def get_estado_subsistema(self):
        return self.__estado_subsistema
    
    def set_variables(self, variables):
        self.__variables = variables

    def set_estado_inicial(self, estado_inicial):
        self.__estado_inicial = estado_inicial

    def set_sistema_candidato(self, background):
        self.__background = background
    
    def set_subsistema(self, subsistema):
        self.__subsistema = subsistema

    def set_estado_subsistema(self, estado_subsistema):
        self.__estado_subsistema = estado_subsistema

    def __repr__(self):
        return (f"Sistema(variables={self.__variables}, estado_inicial={self.__estado_inicial}, "
                f"background={self.__background}, subsistema={self.__subsistema}, "
                f"estado_subsistema={self.__estado_subsistema})")