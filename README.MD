# Quantum VQE Simulator for Molecular Ground States

Simulates the **ground state energy** of simple molecules (H₂, LiH, …) using the **Variational Quantum Eigensolver (VQE)** with **Qiskit**.

## 🔹 Features

- Automatic construction of **parametrized ansatz** (`TwoLocal` or `UCCSD`) for quantum circuits.  
- Measurement of **Pauli strings** with optimization to reuse counts.  
- Accurate calculation of **expectation values** for qubit Hamiltonians.  
- Support for multiple molecules via JSON Hamiltonian files.  
- Classical optimizers can be tested on parametrized circuits.  

## 💡 Key Concepts

- **Wave function parametrization** through ansatz.  
- **Expectation values** for Hamiltonians decomposed into Pauli strings.  
- **Circuit optimization** to reduce measurement overhead.  
- VQE **convergence analysis** and comparison with analytical ground state energy.