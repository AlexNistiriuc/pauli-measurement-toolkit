# ansatz_factory.py

from qiskit.circuit.library import TwoLocal
from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock
from qiskit_nature.second_q.mappers import JordanWignerMapper

def create_TwoLocal(f, num_qubits=4, reps=8, rotation_blocks=['ry'], entanglement='linear', entanglement_blocks=['cx'], parameter_prefix='theta'):
    """
    Create a TwoLocal parameterized quantum circuit (ansatz).
    """
    print('='*50 + f'''
    Ansatz configuration:
    TwoLocal(num_qubits={num_qubits},
             reps={reps},
             rotation_blocks={rotation_blocks},
             entanglement={entanglement},
             entanglement_blocks={entanglement_blocks})\n''' + '='*50, file=f)

    return TwoLocal(
        num_qubits=num_qubits,
        reps=reps,
        rotation_blocks=rotation_blocks,
        entanglement=entanglement,
        entanglement_blocks=entanglement_blocks,
        parameter_prefix=parameter_prefix
    )

def create_UCCSD(f, num_spatial_orbitals, num_elec, reps=1, generalized=False, preserve_spin=True, include_imaginary=True):
    mapper = JordanWignerMapper()
    num_particles = tuple(map(int, num_elec))
    initial_state = HartreeFock(num_spatial_orbitals=num_spatial_orbitals, num_particles=num_particles, qubit_mapper=mapper)

    print('='*50 + f'''
    Ansatz configuration:
    UCCSD(num_spatial_orbitals={num_spatial_orbitals},
          num_particles={num_particles},
          initial_state=\n{initial_state},
          generalized={generalized},
          preserve_spin={preserve_spin},
          include_imaginary={include_imaginary},
          reps={reps})\n''' + '='*50, file=f)

    return UCCSD(
        num_spatial_orbitals=num_spatial_orbitals,
        num_particles=num_particles,
        qubit_mapper=mapper,
        initial_state=initial_state,
        generalized=generalized,
        preserve_spin=preserve_spin,
        include_imaginary=include_imaginary,
        reps=reps
    )
 