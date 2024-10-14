import pandas as pd
import json

class MatrizTPM:
    def __init__(self, json_data):
        """Inicializa la matriz de transición de probabilidades a partir de un JSON."""
        self.data = json.loads(json_data)  # Cargar datos desde JSON
        self.variables = self.data["variables"]
        
        # Crear nombres para filas y columnas
        filas = [f"{var}_t" for var in self.variables]     
        columnas = [f"{var}_t+1" for var in self.variables] 
        
        # Crear el DataFrame con los nombres de filas y columnas
        self.tpm = pd.DataFrame(self.data["TPM"], index=filas, columns=columnas)

    def indexar_matriz(self):
        """Muestra la matriz indexada."""
        print("Matriz de Transición de Probabilidades indexada:")
        print(self.tpm)

# Ejemplo de uso
if __name__ == "__main__":
    json_data = '''
    {
      "condiciones_background": ["e", "f"],
      "subsistema": {
        "t": ["a", "b", "c"],
        "t1": ["b", "c"],
        "estado_actual": [0, 1, 1]
      },
      "estado_actual_total": [0, 1, 1, 0, 1, 0],
      "TPM": [
        [0.2, 0.3, 0.1, 0.0, 0.2, 0.2],
        [0.3, 0.2, 0.2, 0.1, 0.1, 0.1],
        [0.2, 0.2, 0.3, 0.1, 0.1, 0.1],
        [0.1, 0.1, 0.1, 0.3, 0.2, 0.2],
        [0.2, 0.1, 0.1, 0.2, 0.3, 0.1],
        [0.1, 0.2, 0.1, 0.1, 0.1, 0.4]
      ]
    }
    '''
    
    matriz_tpm = MatrizTPM(json_data)
    matriz_tpm.indexar_matriz()
