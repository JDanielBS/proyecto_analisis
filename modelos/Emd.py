import numpy as np
from pyemd import emd
from numpy . typing import NDArray

class Emd:    
    def emd_pyphi (self, u: NDArray [np.float64], v: NDArray [np.float64]) -> float :
        """
        Calculate the Earth Mover ’s Distance (EMD ) between two probability
        stributions u and v.
        The Hamming distance was used as the ground metric .
        """
        if not all( isinstance (arr , np. ndarray ) for arr in [u, v]):
            raise TypeError ("u and v must be numpy arrays .")

        n: int = len(u)
        costs : NDArray [np. float64 ] = np. empty ((n, n))

        for i in range (n):
            costs [i, :i] = [ self.hamming_distance (i, j) for j in range (i)]
            costs [:i, i] = costs [i, :i]
        np. fill_diagonal (costs , 0)

        cost_matrix : NDArray [np. float64 ] = np. array (costs , dtype =np. float64 )
        return emd(u, v, cost_matrix )

    def hamming_distance (self, a: int , b: int) -> int:
        return (a ^ b). bit_count ()