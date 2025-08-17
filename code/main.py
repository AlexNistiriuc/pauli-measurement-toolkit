# main.py

import time
import json
import qiskit as qk
import matplotlib.pyplot as plt
from analitical import analitical_minimum_energy
from simulations import simulation
from vqe_runner import run_vqe


"""
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
"""

def get_input():
    print('\n' + '='*50)
    name = input("Che molecola vuoi analizzare? ")
    filename = f'..\molecules\{name}_sto-3g_qubit_hamiltonian.json' # Path to molecules json
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            print(f"Dati della molecola {name} caricati con successo!\n" + '='*50)
            return json.load(file)
    except FileNotFoundError:
        print(f"Errore: non sono ancora stati caricati dati per questa molecola.")
    except json.JSONDecodeError:
        print(f"Errore: il file {filename} non è un JSON valido.")


def plot_vqe_convergence(energies, min_energy, molecule_name, save_plot=True):
    """
    Plotta la convergenza del VQE
    
    Args:
        energies: Lista delle energie durante l'ottimizzazione
        min_energy: Energia minima analitica
        molecule_name: Nome della molecola
        save_plot: Se salvare il grafico
    """
    
    # Creazione del plot
    plt.figure(figsize=(12, 8))
    
    # Plot principale - energie VQE
    iterations = range(len(energies))
    plt.plot(iterations, energies, 'b-', linewidth=2, label='VQE Energy', alpha=0.8)
    
    # Linea energia minima analitica
    plt.axhline(y=min_energy, color='red', linestyle='--', linewidth=2, 
                label=f'Energia Analitica: {min_energy:.6f}')
    
    # Energia finale VQE
    final_energy = energies[-1]
    plt.axhline(y=final_energy, color='green', linestyle=':', linewidth=2,
                label=f'VQE Finale: {final_energy:.6f}')
    
    # Evidenziare primo e ultimo punto
    plt.scatter([0], [energies[0]], color='blue', s=100, zorder=5, 
                label=f'Inizio: {energies[0]:.6f}')
    plt.scatter([len(energies)-1], [energies[-1]], color='green', s=100, zorder=5,
                label=f'Fine: {final_energy:.6f}')
    
    # Decorazioni
    plt.xlabel('Iterazione', fontsize=12)
    plt.ylabel('Energia (Hartree)', fontsize=12)
    plt.title(f'Convergenza VQE per {molecule_name}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Statistiche nel plot
    error = abs(final_energy - min_energy)
    error_percent = (error / abs(min_energy)) * 100
    
    # Box con statistiche
    stats_text = f'''Statistiche:
• Iterazioni: {len(energies)}
• Errore assoluto: {error:.6f}
• Errore %: {error_percent:.3f}%
• Miglioramento: {energies[0] - energies[-1]:.6f}'''
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Salva il plot
    if save_plot:
        filename = f'{molecule_name}_VQE_convergence.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Plot salvato come: {filename}")
    
    plt.show()


# Main function
def main():
    # Input
    molecule = get_input()
    num_qubits = 4
    shots = 100

    # Divide input's components
    dict = molecule['qubit_hamiltonian']
    pauli_strings = list(dict.keys())
    number_of_qubits = len(pauli_strings[0])

    # Calculate the minimum energy value analitically
    min_energy = analitical_minimum_energy(dict, number_of_qubits)
    print(f"L'energia minima che può assumere la molecola {molecule['name']} e' {min_energy}.")

    start = time.time()
    vqe_result, vqe_energies = run_vqe(molecule['qubit_hamiltonian'], num_qubits, shots)
    end = time.time()
    elapsed = end - start
    
    # Final outputs
    difference = vqe_result.fun - min_energy  
    print(f"L'energia della molecola {molecule['name']} simulata e' {vqe_result.fun}. --> Errore di {difference}.")  
    print(f"Numero di iterazioni: {len(vqe_energies)}")
    print(f"Lista di energie (prime 5): {vqe_energies[:5]}...")
    print(f"Tempo impiegato: {elapsed:.4f} secondi.")
    print('='*50 + '\n')

    print("📊 Creazione grafici...")
    
    # Plot semplice
    plot_vqe_convergence(vqe_energies, min_energy, molecule['name'])


if __name__ == "__main__":
    main()
