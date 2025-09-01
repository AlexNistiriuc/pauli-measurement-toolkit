# main.py

from contextlib import redirect_stdout
import os
import time
import json
import qiskit as qk
import matplotlib.pyplot as plt
from analitical import analitical_minimum_energy
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
    filename = os.path.join("..","molecules", f"{name}_sto-3g_qubit_hamiltonian.json") # Path to molecules json
    print(filename)

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            print(f"Dati della molecola {name} caricati con successo!\n" + '='*50)
            return json.load(file)
    except FileNotFoundError:
        print(f"Errore: non sono ancora stati caricati dati per questa molecola.")
    except json.JSONDecodeError:
        print(f"Errore: il file {filename} non è un JSON valido.")

def plot_vqe_convergence(result, elapsed, energies, min_energy, molecule_name, filename, best_rep, save_plot=True):
    """
    Plotta la convergenza del VQE
    
    Args:
        result: Energia minima sperimentale
        elapsed: Tempo impiegato
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
    
    # Linea energia minima sperimentale
    plt.axhline(y=result, color='blue', linestyle='--', linewidth=2, 
                label=f'Energia minima sperimentale: {result:.6f}')
    
    # Linea energia minima analitica
    plt.axhline(y=min_energy, color='red', linestyle='--', linewidth=2, 
                label=f'Energia minima analitica: {min_energy:.6f}')
    
    # Energia finale VQE
    final_energy = energies[-1]
    plt.axhline(y=final_energy, color='blue', linestyle=':', linewidth=2,
                label=f'VQE Finale: {final_energy:.6f}')
    
    # Evidenziare primo e ultimo punto
    plt.scatter([0], [energies[0]], color='blue', s=100, zorder=5, 
                label=f'Inizio: {energies[0]:.6f}')
    plt.scatter([len(energies)-1], [energies[-1]], color='blue', s=100, zorder=5,
                label=f'Fine: {final_energy:.6f}')
    
    # Evidenziare il punto "migliore"
    plt.scatter(float(best_rep), float(result), color='red', s=100, zorder=5,
                label=f'Migliore: {final_energy:.6f}')
    
    # Decorazioni
    plt.xlabel('Iterazione', fontsize=12)
    plt.ylabel('Energia (Hartree)', fontsize=12)
    plt.title(f'Convergenza VQE per {molecule_name}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Statistiche nel plot
    error = abs(result - min_energy)
    error_percent = (error / abs(min_energy)) * 100
    
    # Box con statistiche
    stats_text = f'''Statistiche:
• Iterazioni: {len(energies)}
• Migliore: {result:.6f}
• Errore assoluto: {error:.6f}
• Errore %: {error_percent:.3f}%
• Miglioramento: {energies[0] - energies[-1]:.6f}
• Tempo impiegato: {elapsed:.6f}'''
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Salva il plot
    if save_plot:
        plt.savefig(os.path.join(filename, "image.png"), dpi=300, bbox_inches='tight')
        print(f"Plot salvato come: {os.path.join(filename, 'image.png')}\n" + '='*50)

    
    plt.show()

# Main function
def main():
    # Input
    molecule = get_input()
    num_qubits = 4
    shots = 20000

    # Formato: YYYY-MM-DD_HH.MM.SS
    timestamp = time.strftime("%Y-%m-%d_%H.%M.%S")
    dirname = os.path.join("results", molecule["name"], timestamp)
    os.makedirs(dirname, exist_ok=True)

    with open(os.path.join(dirname, "file.txt"), 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # Divide input's components
            dict = molecule['qubit_hamiltonian']
            pauli_strings = list(dict.keys())
            number_of_qubits = len(pauli_strings[0])

            # Calculate the minimum energy value analitically
            min_energy = analitical_minimum_energy(dict, number_of_qubits)
            print(f"L'energia minima che puo' assumere la molecola {molecule['name']} e' {min_energy}.")

            start = time.time()
            vqe_result, vqe_energies, best_cirq, best_rep = run_vqe(molecule['qubit_hamiltonian'], num_qubits, shots)
            end = time.time()
            elapsed = end - start
            
            difference = vqe_result.fun - min_energy
            decomposed_circuit = best_cirq.decompose()
            
            # Final outputs
            print(f"Miglior circuito (ripetizione n. {best_rep}):")
            print(decomposed_circuit.draw(fold=60, output='text'))
            print('='*50)
            print(f"L'energia della molecola {molecule['name']} simulata e' {vqe_result.fun}. --> Errore di {difference}.")  
            print(f"Tempo impiegato: {elapsed:.4f} secondi.")
            print('='*50)
            print(f"Hamiltoniana: {dict}")
            print(f"Numero di iterazioni: {len(vqe_energies)}")
            print(f"Lista di energie: {vqe_energies}...")
            print('='*50)
            
            # Plot semplice
            plot_vqe_convergence(vqe_result.fun, elapsed, vqe_energies, min_energy, molecule['name'], dirname, best_rep)
    
    print(f"File salvato come {os.path.join(dirname, 'image.png')}\n")

if __name__ == "__main__":
    main()
