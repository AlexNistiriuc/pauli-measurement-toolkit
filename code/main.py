# main.py

import time
import json
import qiskit as qk
from analitical import analitical_minimum_energy
from simulations import optimized_simulation    # not_optimized_simulation

def get_input():
    print('\n' + '='*50)
    name = input("Che molecola vuoi analizzare? ")
    filename = f'..\molecules\{name}_sto-3g_qubit_hamiltonian.json' #path to molecules' json 
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            print(f"Dati della molecola {name} caricati con successo!\n" + '='*50)
            return json.load(file)
    except FileNotFoundError:
        print(f"Errore: non sono ancora stati caricati dati per questa molecola.")
    except json.JSONDecodeError:
        print(f"Errore: il file {filename} non è un JSON valido.")

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

def main():
    # Input
    molecule = get_input()

    # Divide input's components
    dict = molecule['qubit_hamiltonian']
    pauli_strings = list(dict.keys())
    number_of_qubits = len(pauli_strings[0])
    shots = 1000

    # Calculate the minimum energy value analitically
    min_energy = analitical_minimum_energy(dict, number_of_qubits)

    # Create the cirquit
    cirq = create_quantum_circuit(number_of_qubits)

    # Simulate the cirquit
    start = time.time()
    averages = optimized_simulation(cirq, pauli_strings, shots)
    # averages = not_optimized_simulation(cirq, pauli_strings, shots)
    end = time.time()
    elapsed = end - start
    print("### SIMULATION\'S OUPUT ###")
    print('='*50)

    # Calculate the energy
    # print("\n📊 Expectation values:")
    sim_energy = 0
    for ps in pauli_strings:
        # print(f"<{ps}> = {averages[ps]}")
        sim_energy += averages[ps] * dict[ps]
    print("### EXPECTATION VALUES ###")
    print('='*50)
    
    # Final outputs
    print(f"🎯 L'energia minima che può assumere il valore {min_energy}.")
    print(f"💡 L'energia della molecola {molecule['name']} simulata e' {sim_energy}.")
    print(f"⏱️  Tempo impiegato: {elapsed:.4f} secondi.")
    print('='*50 + '\n')

if __name__ == "__main__":
    main()
