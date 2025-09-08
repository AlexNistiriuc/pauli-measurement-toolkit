# main.py

from contextlib import redirect_stdout
import os
import time
import json
import matplotlib.pyplot as plt
from analitical import analitical_minimum_energy
from vqe_runner import run_vqe


def get_input():
    """
    Prompt user for molecule name and load its Hamiltonian JSON data.
    
    Returns:
        dict: Molecule data loaded from JSON.
    """

    name = input("Which molecule do you want to analyze? ")
    filename = os.path.join("..", "molecules", f"{name}_sto-3g_qubit_hamiltonian.json")
    print(f"Loading molecule data from: {filename}")

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            print(f"Molecule {name} loaded successfully!")
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Data file for {name} not found.")
    except json.JSONDecodeError:
        print(f"Error: {filename} is not a valid JSON file.")


def plot_vqe_convergence(result, elapsed, energies, min_energy, molecule_name, output_dir, best_rep, save_plot=True):
    """
    Plot VQE energy convergence.

    Args:
        result (float): Final VQE energy.
        elapsed (float): Time elapsed during VQE.
        energies (list): List of energies during optimization.
        min_energy (float): Analytical minimum energy.
        molecule_name (str): Molecule name.
        output_dir (str): Directory to save plot.
        best_rep (int): Iteration of the best energy.
        save_plot (bool): Whether to save plot to file.
    """
    plt.figure(figsize=(12, 8))
    iterations = range(len(energies))
    plt.plot(iterations, energies, 'b-', linewidth=2, label='VQE Energy', alpha=0.8)

    # Plot analytical and final energies
    plt.axhline(y=min_energy, color='red', linestyle='--', linewidth=2, label=f'Analytical Minimum: {min_energy:.6f}')
    plt.axhline(y=result, color='blue', linestyle='--', linewidth=2, label=f'Final VQE: {result:.6f}')

    # Highlight start, end, and best iteration
    plt.scatter([0], [energies[0]], color='blue', s=100, label=f'Start: {energies[0]:.6f}')
    plt.scatter([len(energies)-1], [energies[-1]], color='blue', s=100, label=f'End: {energies[-1]:.6f}')
    plt.scatter([best_rep], [result], color='red', s=100, label=f'Best Iteration: {result:.6f}')

    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Energy (Hartree)', fontsize=12)
    plt.title(f'VQE Convergence for {molecule_name}', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)

    # Display stats on plot
    error = abs(result - min_energy)
    error_percent = (error / abs(min_energy)) * 100
    stats_text = f'''Statistics:
• Iterations: {len(energies)}
• Best: {result:.6f}
• Absolute Error: {error:.6f}
• Error %: {error_percent:.3f}%
• Improvement: {energies[0] - energies[-1]:.6f}
• Time elapsed: {elapsed:.6f} s'''
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    if save_plot:
        plt.savefig(os.path.join(output_dir, "vqe_convergence.png"), dpi=300, bbox_inches='tight')
        print(f"Plot saved as: {os.path.join(output_dir, 'vqe_convergence.png')}\n" + '='*50)

    plt.show()


def main():
    print('\n' + '='*50)
    molecule_data = get_input()
    shots=500

    timestamp = time.strftime("%Y-%m-%d_%H.%M.%S")
    output_dir = os.path.join("..", "results", molecule_data["name"], timestamp)
    os.makedirs(output_dir, exist_ok=True)
    f = open(os.path.join(output_dir, "vqe_log.txt"), 'w', encoding='utf-8')

    hamiltonian_dict = molecule_data['qubit_hamiltonian']
    number_of_qubits = len(list(hamiltonian_dict.keys())[0])
    print(f"Data successfully prepared!\n" + '='*50)

    # Calculate analytical minimum
    print(f"....Calculating analitical energy....")
    start_time = time.time()
    min_energy = analitical_minimum_energy(hamiltonian_dict, number_of_qubits)
    end_time = time.time()
    print(f"Minimum (analitical) energy level: {min_energy}\n" + '='*50)
    elapsed_analitical = end_time - start_time

    # Simulating VQE
    print(f"....Starting simulations....")
    start_time = time.time()
    vqe_result, vqe_energies, best_circuit, best_iteration = run_vqe(hamiltonian_dict, number_of_qubits, f, shots=shots)
    end_time = time.time()
    print(f"....Ending simulations....\n" + '='*50)
    elapsed_vqe = end_time - start_time

    energy_diff = vqe_result.fun - min_energy
    decomposed_circuit = best_circuit.decompose()

    with redirect_stdout(f):
        # Print results
        print(f"Hamiltonian: {hamiltonian_dict}")
        print('='*50)
        print(f"Analytical minimum energy for {molecule_data['name']}: {min_energy}")
        print(f"Elapsed time: {elapsed_analitical:.4f} s")
        print('='*50)
        print(f"VQE Energy: {vqe_result.fun} --> Error: {energy_diff}")
        print(f"Shots: {shots}")
        print(f"Time elapsed: {elapsed_vqe:.4f} s")
        print(f"Number of iterations: {len(vqe_energies)}")
        print(f"Energy list: {vqe_energies[:10]} ...")
        print('='*50)
        print(f"Best circuit (iteration {best_iteration}):")
        print(decomposed_circuit.draw(fold=60, output='text'))

        # Plot convergence
        plot_vqe_convergence(vqe_result.fun, elapsed_vqe, vqe_energies, min_energy, molecule_data['name'], output_dir, best_iteration)
    print(f"Log and plot saved in: {output_dir}\n")


if __name__ == "__main__":
    main()
