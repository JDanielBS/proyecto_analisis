from scipy.stats import wasserstein_distance

class Emd:    
    
    def calcularEMD(a: np.ndarray, b: np.ndarray):
        emd_value= wasserstein_distance(a, b)
        return emd_value
        