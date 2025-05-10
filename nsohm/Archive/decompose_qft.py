import pennylane as qml
from pennylane import numpy as np

def generate_qft_gate_sequence(n_qubits=8):
    """Decompose the QFT into Hadamard and controlled-phase (CP) gates."""
    gate_sequence = []
    for target in range(n_qubits):
        # Apply Hadamard to the target qubit
        gate_sequence.append(("H", target))
        # Apply controlled-phase gates from all qubits > target
        for control in range(target + 1, n_qubits):
            angle = np.pi / (2 ** (control - target))
            gate_sequence.append(("CP", float(angle), control, target))
    return gate_sequence

def print_gate_sequence(gates):
    """Nicely prints the gate list."""
    for gate in gates:
        if gate[0] == "H":
            print(f"{gate[0]} on qubit {gate[1]}")
        elif gate[0] == "CP":
            angle_pi_frac = np.round(gate[1] / np.pi, 4)
            print(f"CP({angle_pi_frac}π) from qubit {gate[2]} to {gate[3]}")
        else:
            print("Unknown gate:", gate)

if __name__ == "__main__":
    qft_gates = generate_qft_gate_sequence(n_qubits=8)
    print("Decomposed 8-qubit QFT circuit into:")
    print(f"→ {sum(1 for g in qft_gates if g[0]=='H')} Hadamards")
    print(f"→ {sum(1 for g in qft_gates if g[0]=='CP')} Controlled-Phase gates")
    print()
    print_gate_sequence(qft_gates)
