#vqe_runner.py

import numpy as np
from qiskit import ClassicalRegister
from ansatz_factory import create_ansatz
from scipy.optimize import minimize
from simulations import simulation

def run_vqe(H_dict, num_qubits, file, shots=100):
    """
    ansatz: Circuito parametrico (TwoLocal)
    expectation_func: Funzione che calcola <H> dato il circuito e i parametri
    initial_params: Array iniziale dei parametri
    """

    # Ansatz creation once
    ansatz = create_ansatz(file, num_qubits=num_qubits, reps=3)
    ansatz.add_register(ClassicalRegister(num_qubits, 'c'))

    initial_parameters= np.random.normal(0, 0.1, ansatz.num_parameters)
    energies = []

    n_rep = 0

    best_cirq = None
    min_energy = float('inf')
    best_rep = -1
    
    def objective(params):
        nonlocal best_cirq, min_energy, best_rep, n_rep
        # Using the same ansatz, but with redefined params
        parameterized_circuit = ansatz.assign_parameters(params)

        energy = simulation(parameterized_circuit, H_dict, shots)
        energies.append(energy)

        if energy < min_energy:
            best_cirq = parameterized_circuit
            min_energy = energy
            best_rep = n_rep
            print(f"\tIteration {n_rep} - Energy level: {energy} - NEW BEST")
        else:
            print(f"\tIteration {n_rep} - Energy level: {energy}")

        n_rep += 1

        return energy
    
    result = minimize(objective, initial_parameters, method='COBYLA', options={'maxiter': 200})

    return result, energies, best_cirq, best_rep


if __name__ == "__main__":
    print("🧪 Testing VQE Runner...")
    
    # Test 1: Import dependencies
    try:
        import sys
        from ansatz_factory import create_ansatz
        from simulations import simulation
        print("✅ Import dipendenze: OK")
    except ImportError as e:
        print(f"❌ Import dipendenze: {e}")
        exit(1)
    
    # Test 2: Create ansatz
    try:
        ansatz = create_ansatz(num_qubits=4, reps=3)
        print(f"✅ Creazione ansatz: OK ({ansatz.num_parameters} parametri)")
    except Exception as e:
        print(f"❌ Creazione ansatz: {e}")
        exit(1)
    
    # Test 3: VQE con Hamiltoniana semplice
    print("\n🔬 Test VQE con Hamiltoniana semplice...")
    try:
        # Hamiltoniana semplice per H2
        simple_H = {
            'IIII': -1.0523732,  # Termine costante
            'IIIZ': -0.39793742,  # Z su qubit 3
            'IIZI': -0.39793742,  # Z su qubit 2
            'ZIII': -0.39793742,  # Z su qubit 0
            'ZIIZ': 0.18093119,   # ZZ interaction
        }
        
        # Test veloce con pochi shots e iterazioni
        result, energies = run_vqe(simple_H, num_qubits=4, file=sys.stdout, shots=50)
        
        print(f"✅ VQE Test completato!")
        print(f"   Energia finale: {result.fun:.6f}")
        print(f"   Iterazioni: {len(energies)}")
        print(f"   Convergenza: {'✅' if result.success else '❌'}")
        print(f"   Prime 5 energie: {energies[:5]}")
        
    except Exception as e:
        print(f"❌ Test VQE fallito: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Test completato!")
