
import pennylane as qml
from pennylane import numpy as np

def get_qft_native_sequence(n_qubits=8):
    """Return the 8-qubit QFT as a list of native gates (RX, RY, MS)."""
    seq = []

    def apply_rz_as_rx_ry(phi, qubit):
        # RZ(phi) → RY(pi/2) → RX(phi) → RY(-pi/2)
        seq.append(("RY", np.pi/2, qubit))
        seq.append(("RX", phi, qubit))
        seq.append(("RY", -np.pi/2, qubit))

    def apply_cp_via_ms(phi, control, target):
        # 1) RZ(-φ/2) on control and target
        apply_rz_as_rx_ry(-phi/2, control)
        apply_rz_as_rx_ry(-phi/2, target)
        # 2) Hadamard on target = RX(pi) + RY(pi/2)
        seq.append(("RX", np.pi, target))
        seq.append(("RY", np.pi/2, target))
        # 3) MS(phi) on control & target
        seq.append(("MS", phi, control, target))
        # 4) Hadamard again on target
        seq.append(("RX", np.pi, target))
        seq.append(("RY", np.pi/2, target))

    # Build the QFT
    for target in range(n_qubits):
        # Hadamard on target
        seq.append(("RX", np.pi, target))
        seq.append(("RY", np.pi/2, target))
        # Controlled-phase gates
        for control in range(target+1, n_qubits):
            phi = np.pi / (2 ** (control - target))
            apply_cp_via_ms(phi, control, target)
    print(seq)
    return seq
