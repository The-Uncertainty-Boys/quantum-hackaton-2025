import numpy as np

def rz_to_rx_ry(phi, qubit):
    """Decompose RZ(phi) into RY(π/2) → RX(phi) → RY(-π/2)"""
    return [
        ("RY", np.pi / 2, qubit),
        ("RX", phi, qubit),
        ("RY", -np.pi / 2, qubit),
    ]

def decompose_qft_to_native(n_qubits=8):
    """Decomposes QFT into RX, RY, MS gates only."""
    native_sequence = []
    for target in range(n_qubits):
        # Hadamard on target → RX(π) then RY(π/2)
        native_sequence.append(("RX", np.pi, target))
        native_sequence.append(("RY", np.pi / 2, target))

        # Controlled-phase from each control > target
        for control in range(target + 1, n_qubits):
            phi = np.pi / (2 ** (control - target))

            # CP(phi) decomposition:
            # 1. RZ(-phi/2) on control and target (both)
            native_sequence += rz_to_rx_ry(-phi / 2, control)
            native_sequence += rz_to_rx_ry(-phi / 2, target)

            # 2. Hadamard on target
            native_sequence.append(("RX", np.pi, target))
            native_sequence.append(("RY", np.pi / 2, target))

            # 3. MS(phi) on control-target
            native_sequence.append(("MS", phi, control, target))

            # 4. Hadamard on target again
            native_sequence.append(("RX", np.pi, target))
            native_sequence.append(("RY", np.pi / 2, target))
    return native_sequence


if __name__ == "__main__":
    gates = decompose_qft_to_native(n_qubits=8)
    for g in gates:
        print(g)
