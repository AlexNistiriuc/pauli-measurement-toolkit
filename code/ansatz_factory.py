#ansatz_factory.py

from qiskit.circuit.library import TwoLocal

def create_ansatz(num_qubits=4, reps=3, rotation_blocks='ry', entanglement='full', entanglement_blocks='cx', parameter_prefix='θ'):
    """

    
    """
    


    #returning Ansatz
    return TwoLocal(num_qubits=num_qubits, 
                    reps=reps,
                    rotation_blocks=rotation_blocks, 
                    entanglement=entanglement,
                    entanglement_blocks=entanglement_blocks, 
                    parameter_prefix=parameter_prefix)


