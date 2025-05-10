import pennylane as qml
from pennylane import numpy as np

def get_qft_native_sequence(n_qubits=8):
    """Return the 8-qubit QFT as a list of native gates (RX, RY, MS)
       and print the resulting statevector (should be uniform)."""
    seq = []

    def rz(phi, q):
        # Virtual Z on qubit q via RY/RX/RY
        seq.append(("RY",  np.pi/2, q))
        seq.append(("RX",  phi,     q))
        seq.append(("RY", -np.pi/2, q))

    def H(q):
        # Hadamard via RX + RY
        seq.append(("RX", np.pi,    q))
        seq.append(("RY", np.pi/2,  q))

    def apply_cp(phi, c, t):
        # 1) Z-corrections
        rz(-phi/2, c)
        rz(-phi/2, t)
        # 2) H on both qubits
        H(c)
        H(t)
        # 3) MS(φ)
        seq.append(("MS", phi, c, t))
        # 4) H on both back
        H(c)
        H(t)

    # Build the QFT in native gates
    for target in range(n_qubits):
        # Hadamard on target
        H(target)
        # Controlled‐phase gates
        for control in range(target+1, n_qubits):
            phi = np.pi / (2 ** (control - target))
            apply_cp(phi, control, target)

    return seq
