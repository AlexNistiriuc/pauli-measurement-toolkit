# Pauli String Measurement Simulator

This project uses **Qiskit** to simulate the measurement of Pauli observables (e.g., `XYZI`, `ZZZZ`, `XXYY`) on a given quantum circuit. The code automatically applies the required rotations to align measurements with the Z-basis and computes the expectation values using a quantum simulator.

## 🧪 Features

- Automatically applies pre-measurement rotations for any Pauli basis.
- Simulates the circuit using `qiskit-aer`.
- Computes the expectation value ⟨P⟩ of each Pauli string using shot statistics.
- Supports arbitrary combinations of Pauli operators (`X`, `Y`, `Z`, `I`).

---

## 🛠️ Requirements

Make sure you have Python ≥ 3.8 and install the necessary dependencies:

```bash
pip install qiskit qiskit-aer
