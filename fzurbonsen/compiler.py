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

dev = qml.device("default.mixed", wires=n_qubits)
dev0 = qml.device("default.mixed", wires=n_qubits)
dev1 = qml.device("default.mixed", wires=n_qubits)

ms_gate = np.exp(1j * np.pi / 4) / np.sqrt(2) * np.array([
    [1, 0, 0, -1j],
    [0, 1, -1j, 0],
    [0, -1j, 1, 0],
    [-1j, 0, 0, 1]
])

gates_schedule = []
positions_history = []
time_step = 0  # global time step tracker

def add_to_schedule(gate_type, param, wires):
    """Helper function to add gate to the current time step schedule."""
    while len(gates_schedule) <= time_step:
        gates_schedule.append([])  # Ensure enough time slots
    gates_schedule[time_step].append((gate_type, round(param, 2), wires))

def apply_ms_gate(wire1, wire2, theta):
    qml.QubitUnitary(ms_gate, wires=[wire1, wire2])
    # qml.IsingXX(theta, wires=[wire1, wire2])
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

def apply_controlled_phase_approx(control, target, angle):
    return 0

def apply_controlled_phase(control, target, angle):
    print(f"P, {angle/np.pi}*pi, {target}, {control}")
    # apply_ry_gate(control, -np.pi/2)
    # apply_ry_gate(target, -np.pi/2)
    # apply_ms_gate(control, target, np.pi/4)
    # apply_rx_gate(target, -angle/2)
    # apply_ms_gate(control, target, -np.pi/4)
    # apply_ry_gate(control, np.pi/2)
    # apply_ry_gate(target, np.pi/2)

    apply_ry_gate(control, -np.pi/2)
    apply_ry_gate(target, np.pi/2)
    apply_rx_gate(control, -np.pi/2)
    apply_rx_gate(target, np.pi/2)
    apply_ms_gate(target, control, angle/4)
    apply_ry_gate(control, np.pi/2)
    apply_ry_gate(target, -np.pi/2)

    # apply_ry_gate(control, -np.pi/2)
    # apply_ry_gate(target, -np.pi/2)
    # apply_ms_gate(control, target, np.pi/4)        # Entangle
    # apply_rx_gate(target, -angle / 2)              # Apply phase on target
    # apply_ms_gate(control, target, -np.pi/4)       # Undo entanglement
    # apply_ry_gate(control, np.pi/2)
    # apply_ry_gate(target, np.pi/2)

    # qml.ControlledPhaseShift(angle, wires=[control, target])
    print("\n")

@qml.qnode(dev)
def qft_like_circuit():
    global time_step

    for target in range(n_qubits):
        apply_hadamard_approx(target)

        # Move to the next time step
        time_step += 1

        for control in range(target + 1, n_qubits):
            angle = np.pi / (2 ** (control - target))
            apply_controlled_phase_approx(control, target, angle)

        # Move to the next time step after controlled-phase set
        time_step += 1

    # print(qml.density_matrix(wires=range(n_qubits)))
    return qml.density_matrix(wires=range(n_qubits))

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
state = qft_circuit()
print(state)
# print("Quantum state after approximate QFT with RX, RY, MS:", state)

# print(qml.density_matrix(wires=range(8)))

bench = qft_bench()
print(bench)

# print_gate_schedule(gates_schedule)

# Create the trap graph
graph = trap.create_trap_graph()

verifier.verifier(positions_history, gates_schedule, graph)


print("done")
