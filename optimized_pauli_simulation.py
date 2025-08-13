# optimized_pauli_simulation.py

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
cirq.barrier()

# Function to apply basis-changing gates
def apply_rotations_pauli_string(qc, pauli_string):
    for i, pauli in enumerate(pauli_string):
        if pauli == 'I' or pauli == 'Z':
            continue
        elif pauli == 'X':
            qc.h(qc.qubits[i])
        elif pauli == 'Y':
            qc.sdg(qc.qubits[i])
            qc.h(qc.qubits[i])

# Function to measure qubits in Z-basis
def measure_pauli_string(qc, pauli_string):
    for i, pauli in enumerate(pauli_string):
        if pauli != 'I':
            qc.measure(qc.qubits[i], qc.clbits[i])

# Check if base can be reused
def can_reuse_measurements(pauli_string, stored_strings):
    for string in stored_strings:
        is_reusable = True
        for a, b in zip(pauli_string, string):
            if a != b and (a not in ['I', 'Z'] or b not in ['I', 'Z']):
                is_reusable = False
                break
        if is_reusable:
            return string
    return None

# Main simulation
def simulate_pauli_strings(qc, pauli_strings, number_of_shots):
    reusable_data = {}
    results = {}

    for pauli_string in pauli_strings:
        if len(pauli_string) != len(qc.qubits):
            raise ValueError(f"Pauli string {pauli_string} length mismatch")
        for operator in pauli_string:
            if operator not in ['I', 'X', 'Y', 'Z']:
                raise ValueError(f"Invalid operator {operator}")

        base = can_reuse_measurements(pauli_string, reusable_data.keys())
        if base is not None:
            counts = reusable_data[base]
            print(f"Reusing measurement from Pauli string: {base} for {pauli_string}")
        else:
            temp_circ = qc.copy()
            temp_circ.barrier()
            apply_rotations_pauli_string(temp_circ, pauli_string)
            temp_circ.barrier()
            measure_pauli_string(temp_circ, pauli_string)
            

            # Print circuit for this Pauli string
            print(f"\nMeasuring new Pauli string: {pauli_string}")
            print(temp_circ.draw(output='text'))
            if not all(c == 'I' for c in pauli_string):
                simulator = AerSimulator()
                temp_circ = qk.transpile(temp_circ, simulator)
                job = simulator.run(temp_circ, shots=number_of_shots)
                result = job.result()
                counts = result.get_counts()
                reusable_data[pauli_string] = counts

        # Expectation value

        if all(c == 'I' for c in pauli_string):
            average = 1
        else:
            total = 0
            for outcome in counts:
                eigenvalue = 1
                for i, bit in enumerate(outcome):
                    if pauli_string[i] != 'I' and bit == '1':
                        eigenvalue *= -1
                total += counts[outcome] * eigenvalue
            average = total / number_of_shots

        results[pauli_string] = average
    return results

# Input
pauli_strings = ['XXXX', 'XYZZ', 'ZZZZ', 'ZIZZ', 'ZZII']
shots = 1000

# Run
averages = simulate_pauli_strings(cirq, pauli_strings, shots)

# Print final results
print("\n📊 Expectation values:")
for ps in pauli_strings:
    print(f"<{ps}> = {averages[ps]}")

# Calculation the execution's time
end = time.time()
elapsed = end - start
print(f"Tempo impiegato: {elapsed:.4f} seconds")
