# simulations.py

import qiskit as qk
from qiskit_aer import AerSimulator

def controls(pauli_str, qc):
    if len(pauli_str) != len(qc.qubits):
        raise ValueError(f"Pauli string {pauli_str} length mismatch")
    for operator in pauli_str:
        if operator not in ['I', 'X', 'Y', 'Z']:
            raise ValueError(f"Invalid operator {operator}")

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
                is_reusable = False # Check if the strings need the same rotations
                break
        if is_reusable:
            return string
    return None

# Given a qc and a pauli_str, get the outputs
def get_output(qc, pauli_str, shots):
    # Copy the base circuit
    temp_cirq = qc.copy()
    apply_rotations_pauli_string(temp_cirq, pauli_str)
    temp_cirq.barrier()
    measure_pauli_string(temp_cirq, pauli_str)

    # Print circuit for this Pauli string
    # print(f"\nMisurando la nuova stringa di Pauli: {pauli_str}")
    # print(temp_cirq.draw(output='text'))
    simulator = AerSimulator()
    temp_cirq = qk.transpile(temp_cirq, simulator)
    job = simulator.run(temp_cirq, shots=shots)
    result = job.result()
    counts = result.get_counts()

    return counts

# Calculate the expected value given a pauli_str and its counts
def expectation_value(pauli_str, counts, shots):
    total = 0
    for outcome in counts:
        eigenvalue = 1
        for i, bit in enumerate(outcome):
            if pauli_str[i] != 'I' and bit == '1':
                eigenvalue *= -1
        total += counts[outcome] * eigenvalue
    return total / shots

# Not optimized version
def not_optimized(qc, pauli_strings, shots):
    results = {}

    for pauli_str in pauli_strings:
        # Control the string lenght and composition
        controls(pauli_str=pauli_str, qc=qc)

        # If all-I string set result = 1
        if all(c == 'I' for c in pauli_str):
            results[pauli_str] = 1
            continue
        
        # Get the circuit output
        counts = get_output(qc, pauli_str, shots=shots)
        # Expectation value
        results[pauli_str] = expectation_value(pauli_str, counts, shots)

    return results

# Optimized version
def optimized(qc, pauli_strings, shots):
    reusable_data = {}
    results = {}

    for pauli_str in pauli_strings:
        # Control the string lenght and composition
        controls(pauli_str=pauli_str, qc=qc)

        # If all-I string set result = 1
        if all(c == 'I' for c in pauli_str):
            results[pauli_str] = 1
            continue

        base = can_reuse_measurements(pauli_str, reusable_data.keys())
        if base is not None:
            # Reuse the circuit outputs
            counts = reusable_data[base]
            results[pauli_str] = expectation_value(pauli_str, counts, shots)
            # print(f"Riutilizzando le misurazioni della stringa di Pauli {base} per {pauli_str}")
        else:
            # Get the circuit output
            counts = get_output(qc, pauli_str, shots=shots)
            reusable_data[pauli_str] = counts
            # Expectation value
            results[pauli_str] = expectation_value(pauli_str, counts, shots)
            

    return results

# Main function to compute expectation values of Pauli strings in the given quantum circuit
def simulation(qc, dict, shots):
    averages = optimized(qc, list(dict.keys()), shots)          # optimized version
    # averages = not_optimized(qc, list(dict.keys()), shots)    # not optimized version

    # Calculate the energy
    # print("\nExpectation values:")
    sim_energy = 0
    for ps in list(dict.keys()):
        # print(f"<{ps}> = {results[ps]}")
        sim_energy += averages[ps] * dict[ps]

    return sim_energy
