# optimized_pauli_simulation.py

import time
import json
import qiskit as qk
from qiskit_aer import AerSimulator

def create_quantum_circuit(num):
    # Create a n-qubit quantum circuit with classical bits for measurement
    q = qk.QuantumRegister(num)
    c = qk.ClassicalRegister(num)
    cirq = qk.QuantumCircuit(q, c)

    # Apply X gates to alternating qubits
    for i in range(num):
        if (i%2 == 0):
            cirq.x(i)

    cirq.barrier()

    return cirq

# Function to apply basis-changing gates so that Pauli measurements can be done in Z-basis
def apply_rotations_pauli_string(qc, pauli_str):
    for i, pauli in enumerate(pauli_str):
        if pauli == 'I' or pauli == 'Z':
            continue  # No rotation needed
        elif pauli == 'X':
            qc.h(qc.qubits[i])  # Rotate X to Z
        elif pauli == 'Y':
            qc.sdg(qc.qubits[i])  # S†
            qc.h(qc.qubits[i])    # Rotate Y to Z

# Function to measure qubits in Z-basis
def measure_pauli_string(qc, pauli_str):
    for i, pauli in enumerate(pauli_str):
        if pauli != 'I':  # Only measure non-identity terms
            qc.measure(qc.qubits[i], qc.clbits[i])

# Check if base can be reused
def can_reuse_measurements(pauli_str, stored_strings):
    for string in stored_strings:
        is_reusable = True
        for a, b in zip(pauli_str, string):
            if a != b and (a not in ['I', 'Z'] or b not in ['I', 'Z']):
                is_reusable = False # check if the strings need the same rotations
                break
        if is_reusable:
            return string
    return None

# Main function to compute expectation values of Pauli strings
def simulate_pauli_strings(qc, pauli_strings, number_of_shots):
    reusable_data = {}
    results = {}

    for pauli_str in pauli_strings:
        if len(pauli_str) != len(qc.qubits):
            raise ValueError(f"Pauli string {pauli_str} length mismatch")
        for operator in pauli_str:
            if operator not in ['I', 'X', 'Y', 'Z']:
                raise ValueError(f"Invalid operator {operator}")

        base = can_reuse_measurements(pauli_str, reusable_data.keys())
        if base is not None:
            counts = reusable_data[base]
            print(f"♻️ Reusing measurement from Pauli string: {base} for {pauli_str}")
        else:
            # Copy the base circuit
            temp_cirq = qc.copy()
            apply_rotations_pauli_string(temp_cirq, pauli_str)
            temp_cirq.barrier()
            measure_pauli_string(temp_cirq, pauli_str)

            # Print circuit for this Pauli string
            print(f"\n🔍 Measuring new Pauli string: {pauli_str}")
            print(temp_cirq.draw(output='text'))
            if not all(c == 'I' for c in pauli_str):
                simulator = AerSimulator()
                temp_cirq = qk.transpile(temp_cirq, simulator)
                job = simulator.run(temp_cirq, shots=number_of_shots)
                result = job.result()
                counts = result.get_counts()
                reusable_data[pauli_str] = counts

        # Expectation value
        if all(c == 'I' for c in pauli_str):
            average = 1
        else:
            total = 0
            for outcome in counts:
                eigenvalue = 1
                for i, bit in enumerate(outcome):
                    if pauli_str[i] != 'I' and bit == '1':
                        eigenvalue *= -1
                total += counts[outcome] * eigenvalue
            average = total / number_of_shots

        results[pauli_str] = average

    return results

def main():
    # Start time to notice how much time does it take
    start = time.time()

    # Input
    with open('H2_sto-3g_qubit_hamiltonian.json', 'r', encoding='utf-8') as file:
        molecule = json.load(file)
    dict = molecule['qubit_hamiltonian']
    pauli_strings = list(dict.keys())
    number_of_qubits = len(pauli_strings[0])
    shots = 1000

    # Run
    cirq = create_quantum_circuit(number_of_qubits)
    averages = simulate_pauli_strings(cirq, pauli_strings, shots)

    # Print final results
    print("\n📊 Expectation values:")
    energy = 0
    for ps in pauli_strings:
        print(f"<{ps}> = {averages[ps]}")
        energy += averages[ps] * dict[ps]
    print(f"\n💡 L'energia della molecola {molecule['name']} e' {energy}")

    # Calculation the execution's time
    end = time.time()
    elapsed = end - start
    print(f"⏱️  Tempo impiegato: {elapsed:.4f} secondi.\n")

if __name__ == "__main__":
    main()
