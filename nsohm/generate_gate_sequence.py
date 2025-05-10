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

    # --- run and print the resulting statevector ---
    dev = qml.device("default.qubit", wires=n_qubits)
    @qml.qnode(dev)
    def circuit():
        for g in seq:
            name = g[0]
            if name == "RX":
                _, a, q = g; qml.RX(a, wires=q)
            elif name == "RY":
                _, a, q = g; qml.RY(a, wires=q)
            else:  # MS
                _, a, c, t = g; qml.IsingXX(a, wires=[c, t])
        return qml.state()

    state = circuit()
    print("\n--- Compiled QFT Output Statevector ---")
    for idx, amp in enumerate(state):
        print(f"|{idx:03}>: {amp:.4f}")
    print(f"(All {len(state)} amplitudes should be 0.0625+0j.)\n")

    return seq
