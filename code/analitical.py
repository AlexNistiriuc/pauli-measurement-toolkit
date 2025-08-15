# analitical.py

import numpy as np

# Compute the matrix
def pstr_to_matrix(pauli_str):
    matrix = np.array([1])                      # Initial matrix
    pauli_dict = {
        'I' : np.array([[1, 0], [0, 1]]),       # I operator
        'X' : np.array([[0, 1], [1, 0]]),       # X operator
        'Y' : np.array([[0, -1j], [1j, 0]]),    # Y operator
        'Z' : np.array([[1, 0], [0, -1]])       # Z operator
        }
    for c in pauli_str:
        matrix = np.kron(matrix, pauli_dict[c]) # Tensor product
    return matrix

# Main function to calculate the expected minimun energy
def analitical_minimum_energy(dict, n):
    H = np.zeros((2**n, 2**n), dtype=complex)   # Starting 0-matrix
    for ps in list(dict.keys()):
        H += dict[ps] * pstr_to_matrix(ps)      # Add weighted matrix
    eigenvalues = np.linalg.eigh(H)[0]          # Find eigenvalues
    return eigenvalues[0]                       # Return first (and minimum) eigenvalue
