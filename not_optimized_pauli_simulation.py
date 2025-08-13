# pauli_simulation.py

import time
import qiskit as qk
from qiskit_aer import AerSimulator

# Start time to notice how much time does it take
start = time.time()

# Create a 4-qubit quantum circuit with classical bits for measurement
q = qk.QuantumRegister(4)
c = qk.ClassicalRegister(4)
cirq = qk.QuantumCircuit(q, c)

# Prepare the initial state: apply X-gates
cirq.x(q[0])  # Flip qubit 0 to |1⟩
cirq.x(q[2])  # Flip qubit 2 to |1⟩

# Add a barrier for clarity
cirq.barrier()

# Function to apply basis-changing gates so that Pauli measurements can be done in Z-basis
def apply_rotations_pauli_string(qc, pauli_string):
    for i, pauli in enumerate(pauli_string):
        if pauli == 'I' or pauli == 'Z':
            continue  # No rotation needed
        elif pauli == 'X':
            qc.h(qc.qubits[i])  # Rotate X to Z
        elif pauli == 'Y':
            qc.sdg(qc.qubits[i])  # S†
            qc.h(qc.qubits[i])    # Rotate Y to Z

# Function to measure qubits in the Z-basis
def measure_pauli_string(qc, pauli_string):
    for i, pauli in enumerate(pauli_string):
        if pauli != 'I':  # Only measure non-identity terms
            qc.measure(qc.qubits[i], qc.clbits[i])

# Main function to compute expectation values of Pauli strings
def simulate_pauli_strings(qc, pauli_strings, number_of_shots):
    results = []

    for pauli_string in pauli_strings:
        # Copy the base circuit
        temp_cirq = qc.copy()
        temp_cirq.barrier()

        # Apply rotations and measurements
        apply_rotations_pauli_string(temp_cirq, pauli_string)
        temp_cirq.barrier()
        measure_pauli_string(temp_cirq, pauli_string)

        # Transpile and simulate
        simulator = AerSimulator()
        temp_cirq = qk.transpile(temp_cirq, simulator)
        job = simulator.run(temp_cirq, shots=number_of_shots)
        result = job.result()
        counts = result.get_counts()

        # Compute expectation value
        total = 0
        for outcome in counts:
            eigenvalue = 1
            for bit in outcome:
                if bit == '1':
                    eigenvalue *= -1
            total += counts[outcome] * eigenvalue
        average = total / number_of_shots
        results.append(average)

    return results

# List of Pauli strings to measure
pauli_strings = ['XXXX', 'XYZZ', 'ZZZZ', 'ZIZZ', 'ZZII']
# Number of simulation shots
shots = 100000

# Run simulation
averages = simulate_pauli_strings(cirq, pauli_strings, shots)

# Print results
for i, pauli_string in enumerate(pauli_strings):
    print(f"<{pauli_string}> = {averages[i]}")

# Calculation the execution's time
end = time.time()
elapsed = end - start
print(f"Tempo impiegato: {elapsed:.4f} seconds")