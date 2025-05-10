# custom imports
import pennylane as qml
from functools import partial
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append("..")

# import official files
import trap
#import verifier
import verifier_modified


def hadamard_rx_ry(wire):
    qml.RY(np.pi/2, wires=wire)
    qml.RX(np.pi, wires=wire)

def RZ_with_RX_RY(phi, wire):
    """Implements RZ(phi) using RX and RY gates."""
    qml.RX(np.pi/2, wires=wire)
    qml.RY(phi, wires=wire)
    qml.RX(-np.pi/2, wires=wire)

def controlled_phase_isingxx(control, target, phi):
        # Apply RZ(phi/2) to target using RX/RY decomposition
    RZ_with_RX_RY(phi/2, target)
    
    # Basis change to map MS to CZ
    qml.RY(-np.pi/2, wires=control)
    qml.RY(-np.pi/2, wires=target)
    
    # MS(pi/2) gate (IsingXX)
    qml.IsingXX(np.pi/2, wires=[control, target])
    
    # Undo basis change
    qml.RY(np.pi/2, wires=control)
    qml.RY(np.pi/2, wires=target)
    
    # Apply RZ(-phi/2) to target using RX/RY decomposition
    RZ_with_RX_RY(-phi/2, target)

def qft_rx_ry_isingxx(wires):
    n = len(wires)
    for j in range(n):
        hadamard_rx_ry(wires[j])
        for k in range(2, n-j+1):
            target = j + k - 1
            if target < n:
                angle = np.pi / (2 ** (k-1))
                controlled_phase_isingxx(wires[j], wires[target], angle)
    # Optional: Reverse qubit order with SWAPs
    for i in range(n//2):
        qml.SWAP(wires=[wires[i], wires[n-i-1]])

dev = qml.device('default.qubit', wires=8)

# --- Custom QFT circuit ---
@qml.qnode(dev)
def custom_qft_circuit():
    # Prepare a computational basis state, e.g. |1>
    qml.PauliX(0)
    qml.PauliX(1)
    qft_rx_ry_isingxx(list(range(8)))
    # qml.templates.QFT(wires=list(range(8)))
    return qml.state()

# --- Built-in QFT circuit ---
@qml.qnode(dev)
def builtin_qft_circuit():
    # Prepare the same initial state for fair comparison
    qml.PauliX(wires=1)
    qml.templates.QFT(wires=list(range(8)))
    return qml.state()

# --- Run and compare ---
state_custom = custom_qft_circuit()
state_builtin = builtin_qft_circuit()

# Compute the fidelity (overlap) between the two output states
fidelity = np.abs(np.vdot(state_custom, state_builtin))**2

print("Fidelity between custom QFT and built-in QFT:", fidelity)
print("Are the states numerically close?", np.allclose(state_custom, state_builtin))



# fig, ax = qml.draw_mpl(circuit)()
# fig.show()  # or plt.show()
# input("Press Enter to exit...")