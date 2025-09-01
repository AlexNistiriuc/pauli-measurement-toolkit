#ansatz_factory.py

from qiskit.circuit.library import TwoLocal

def create_ansatz(num_qubits=4, reps=8, rotation_blocks=['ry'], entanglement='linear', entanglement_blocks=['cx'], parameter_prefix='theta'):
    
    print('='*50 + f"\nL'ansatz utilizzato e' del tipo:\n\tTwoLocal(num_qubits={num_qubits},\n\t\t\t reps={reps},\n\t\t\t rotation_blocks={rotation_blocks},\n\t\t\t entanglement={entanglement},\n\t\t\t entanglement_blocks='cz')\n" + '='*50)

    #returning Ansatz
    return TwoLocal(num_qubits=num_qubits, 
                    reps=reps,
                    rotation_blocks=rotation_blocks, 
                    entanglement=entanglement,
                    entanglement_blocks=entanglement_blocks, 
                    parameter_prefix=parameter_prefix)


