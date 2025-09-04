# ansatz_factory.py

from qiskit.circuit.library import TwoLocal

def create_ansatz(num_qubits=4, reps=8, rotation_blocks=['ry'], entanglement='linear', entanglement_blocks=['cx'], parameter_prefix='theta'):
    """
    Create a TwoLocal parameterized quantum circuit (ansatz).
    """
    print('='*50 + f"\nAnsatz configuration:\nTwoLocal(num_qubits={num_qubits}, reps={reps}, rotation_blocks={rotation_blocks}, entanglement={entanglement}, entanglement_blocks={entanglement_blocks})\n" + '='*50)

    return TwoLocal(
        num_qubits=num_qubits,
        reps=reps,
        rotation_blocks=rotation_blocks,
        entanglement=entanglement,
        entanglement_blocks=entanglement_blocks,
        parameter_prefix=parameter_prefix
    )
