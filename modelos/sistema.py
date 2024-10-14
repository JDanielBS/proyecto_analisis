import csv
import json

class Sistema:

    def __init__(self):
        self.__estado_inicial
        self.__background
        self.__subsistema_futuro
        self.__subsistema_presente

    def set_with_csv(self, ruta):
        with open(ruta, mode='r') as archivo:
            lector = csv.reader(archivo)
            fila = next(lector)
            if len(fila) >= 4:
                self.__estado_inicial = fila[1].strip()
                self.__background = fila[2].strip()
                self.__subsistema_futuro = fila[3].strip()
                self.__subsistema_presente = fila[4].strip()
            else:
                raise ValueError("El archivo CSV no tiene suficientes columnas")
            
    def set_with_json(self, ruta):
        with open(ruta, mode='r') as archivo:
            contenido = json.load(archivo)
            self.__estado_inicial = contenido["estado_inicial"]
            self.__background = contenido["background"]
            self.__subsistema = contenido["subsistema"]

    def get_estado_inicial(self):
        return self.__estado_inicial
    
    def get_sistema_candidato(self):
        return self.__background
    
    def get_subsistema_presente(self):
        return self.__subsistema_presente
    
    def get_subsistema_futuro(self):
        return self.__subsistema_futuro

    def set_estado_inicial(self, estado_inicial):
        self.__estado_inicial = estado_inicial

    def set_sistema_candidato(self, background):
        self.__background = background
    
    def set_subsistema_presente(self, subsistema_presente):
        self.__subsistema_presente = subsistema_presente

    def set_subsistema_futuro(self, subsistema_futuro):
        self.__subsistema_futuro = subsistema_futuro

    def __repr__(self):
        return (f"Estado_inicial={self.__estado_inicial}, "
                f"background={self.__background}, subsistema_presente={self.__subsistema_presente}, "
                f"subsistema_futuro={self.__subsistema_futuro})")