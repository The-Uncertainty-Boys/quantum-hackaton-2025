import sys
import os
import networkx as nx
import matplotlib.pyplot as plt
import pennylane as qml
from pennylane import numpy as np

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trap  # Import trap module
import verifier # Import verifier module

n_qubits = 8

n_ = 0.01

dev = qml.device("default.mixed", wires=n_qubits)
dev0 = qml.device("default.mixed", wires=n_qubits)
dev1 = qml.device("default.mixed", wires=n_qubits)

gates_schedule = []
positions_history = []
time_step = 0  # global time step tracker

def add_to_schedule(gate_type, param, wires):
    """Helper function to add gate to the current time step schedule."""
    while len(gates_schedule) <= time_step:
        gates_schedule.append([])  # Ensure enough time slots
    gates_schedule[time_step].append((gate_type, param, wires))

def build_ms_gate(theta):
    I = np.eye(2)
    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)
    return np.cos(theta / 2) * np.eye(4) - 1j * np.sin(theta / 2) * XX

def apply_ms_gate(wire1, wire2, theta):
    U = build_ms_gate(theta)
    qml.QubitUnitary(U, wires=[wire1, wire2])
    print(f"MS, {theta/np.pi}*pi, [{wire1}, {wire2}]")
    add_to_schedule("MS", theta, (wire1, wire2))

def apply_rx_gate(wire, theta):
    qml.RX(theta, wires=wire)
    print(f"RX, {theta/np.pi}*pi, {wire}")
    add_to_schedule("RX", theta, wire)

def apply_ry_gate(wire, theta):
    qml.RY(theta, wires=wire)
    print(f"RY, {theta/np.pi}*pi, {wire}")
    add_to_schedule("RY", theta, wire)

def apply_hadamard_approx(wire):
    print("H:")
    apply_ry_gate(wire, np.pi/2)
    apply_rx_gate(wire, np.pi)
    print("\n")

def apply_isingXX_gate(control, target, theta):
    apply_ry_gate(target, -np.pi/2)
    apply_ry_gate(control, -np.pi/2)
    apply_ms_gate(control, target, theta)
    apply_ry_gate(target, np.pi/2)
    apply_ry_gate(control, np.pi/2)

def apply_cnot_approx(control, target):
    apply_ry_gate(control, np.pi/2)
    # apply_ms_gate(control, target, np.pi/4*n_)
    qml.IsingXX(np.pi/2*n_, wires=[control, target])
    # apply_isingXX_gate(control, target, np.pi/4*n_)
    apply_rx_gate(target, -np.pi/2*n_)
    apply_rx_gate(control, -np.pi/2*n_)
    apply_ry_gate(control, -np.pi/2)

def apply_rz_approx(wire, theta):
    apply_ry_gate(wire, np.pi/2)
    apply_rx_gate(wire, theta)
    apply_ry_gate(wire, -np.pi/2)

def apply_controlled_phase(control, target, angle):
    print(f"P, {angle/np.pi}*pi, {target}, {control}")
    apply_ry_gate(control, -np.pi/2)
    apply_ry_gate(target, -np.pi/2*n_)

    apply_ms_gate(control, target, np.pi/4*n_)
    apply_rx_gate(target, -angle/2*n_)
    apply_ms_gate(control, target, -np.pi/4*n_)

    apply_ry_gate(control, np.pi/2)
    apply_ry_gate(target, np.pi/2*n_)

    # apply_ry_gate(control, -np.pi/2)
    # apply_ry_gate(target, np.pi/2)
    # apply_rx_gate(control, -np.pi/2)
    # apply_rx_gate(target, np.pi/2)
    # apply_ms_gate(target, control, angle/4)
    # apply_ry_gate(control, np.pi/2)
    # apply_ry_gate(target, -np.pi/2)

    # apply_ry_gate(control, -np.pi/2)
    # apply_ry_gate(target, -np.pi/2)
    # apply_ms_gate(control, target, np.pi/4)        # Entangle
    # apply_rx_gate(target, -angle / 2)              # Apply phase on target
    # apply_ms_gate(control, target, -np.pi/4)       # Undo entanglement
    # apply_ry_gate(control, np.pi/2)
    # apply_ry_gate(target, np.pi/2)

    # apply_cnot_approx(control, target)
    # apply_rz_approx(target, angle)
    # apply_cnot_approx(control, target)

    # qml.ControlledPhaseShift(angle, wires=[control, target])
    print("\n")

@qml.qnode(dev0)
def qft_circuit():
    global time_step

    for target in range(n_qubits):
        apply_hadamard_approx(target)

        time_step += 1

        for control in range(target + 1, n_qubits):
            angle = np.pi/ (2 ** (control - target))
            apply_controlled_phase(control, target, angle)

        time_step += 1
    
    return qml.density_matrix(wires=range(n_qubits))

@qml.qnode(device=dev1)
def qft_bench():
    qml.QFT(wires=range(n_qubits))
    return qml.density_matrix(wires=range(n_qubits))

def print_gate_schedule(schedule):
    print("Gate Schedule:\n")
    for t, gates in enumerate(schedule):
        if gates:
            print(f"  t = {t}")
            for gate in gates:
                gate_type, param, wires = gate
                wire_str = f"{wires}" if isinstance(wires, tuple) else f"{wires}"
                print(f"   → {gate_type}({param}) on wire(s) {wire_str}")
        else:
            print(f"🕒 t = {t}")
            print("   → No gates applied")
    print()


# Run and get final state
# state = qft_like_circuit()
np.set_printoptions(linewidth=200, precision=5, suppress=True)
state = qft_circuit()
# print(state)
# print("Quantum state after approximate QFT with RX, RY, MS:", state)

# print(qml.density_matrix(wires=range(8)))

bench = qft_bench()
# print(bench)

np.set_printoptions(threshold=np.inf, linewidth=np.inf, precision=5, suppress=True)


# with open("qft_output.txt", "w") as f:
#     f.write("State (Custom QFT Approx):\n")
#     f.write(str(state) + "\n\n")
    
#     f.write("Bench (qml.QFT):\n")
#     f.write(str(bench) + "\n\n")

np.set_printoptions(threshold=200, linewidth=200, precision=5, suppress=True)
    

print("Max difference:", np.max(np.abs(state - bench)))
print("Are they close?", np.allclose(state, bench, atol=1e-3))
print("Fidelity: ", np.abs(np.vdot(state, bench)))

diff_matrix = np.abs(state - bench)
max_diff_idx = np.unravel_index(np.argmax(diff_matrix), diff_matrix.shape)
print(f"Largest difference at index {max_diff_idx}:")
print(f"state: {state[max_diff_idx]}")
print(f"bench: {bench[max_diff_idx]}")

ms = build_ms_gate(np.pi/4*n_)

print(ms)

# print_gate_schedule(gates_schedule)

# Create the trap graph
graph = trap.create_trap_graph()

print(gates_schedule)

verifier.verifier(positions_history, gates_schedule, graph)


print("done")
