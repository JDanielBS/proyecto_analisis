from scipy.stats import wasserstein_distance
import numpy as np
from numpy . typing import NDArray

class Emd:    
    
    def calcularEMD(self, u: NDArray[np.float64], v: NDArray[np.float64]):
        emd_value= wasserstein_distance(u, v)
        return emd_value
        