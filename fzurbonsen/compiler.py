import sys
import os
import networkx as nx
import matplotlib.pyplot as plt
import pennylane as qml
from pennylane import numpy as np

import QGate
import router
import scheduler

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trap  # Import trap module
import verifier # Import verifier module


n_qubits = 8
gate_lists = [[] for _ in range(n_qubits)]
gate_id = 0
n_ms = 0

n_ = 0.01

dev = qml.device("default.mixed", wires=n_qubits)
dev0 = qml.device("default.mixed", wires=n_qubits)
dev1 = qml.device("default.mixed", wires=n_qubits)

gates_schedule = []
positions_history = []
time_step = 0  # global time step tracker

def add_to_schedule(gate_type, param, wires):
    global gate_id 
    global n_ms

    while len(gates_schedule) <= time_step:
        gates_schedule.append([])  # Ensure enough time slots
    gates_schedule[time_step].append((gate_type, param, wires))

    if gate_type in ["RX", "RY"]:
        gate_lists[wires].append(QGate.QGate(gate_id, gate_type, wires, theta=param))
        gate_id += 1
    elif gate_type == "MS":
        w1, w2 = wires
        gate_lists[w1].append(QGate.QGate(gate_id, gate_type, w1, w2, param))
        gate_lists[w2].append(QGate.QGate(gate_id, gate_type, w2, w1, param))
        gate_lists[w1][-1].ms_id = n_ms
        gate_lists[w2][-1].ms_id = n_ms
        n_ms += 1
        gate_id += 1
    else:
        raise AssertionError(f"Invalid gate type {gate_type}!")



def build_ms_gate(theta):
    I = np.eye(2)
    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)
    return np.cos(theta / 2) * np.eye(4) - 1j * np.sin(theta / 2) * XX

def apply_ms_gate(wire1, wire2, theta):
    U = build_ms_gate(theta)
    qml.QubitUnitary(U, wires=[wire1, wire2])
    add_to_schedule("MS", theta, (wire1, wire2))

def apply_rx_gate(wire, theta):
    qml.RX(theta, wires=wire)
    add_to_schedule("RX", theta, wire)

def apply_ry_gate(wire, theta):
    qml.RY(theta, wires=wire)
    add_to_schedule("RY", theta, wire)

def apply_hadamard_approx(wire):
    apply_ry_gate(wire, np.pi/2)
    apply_rx_gate(wire, np.pi)

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

def print_adjacency_and_gates(adj_mat, gates):
    print("Adjacency Matrix:")
    for row in adj_mat:
        print(" ".join(str(val) for val in row))

    print("\nGates List:")
    for gate in gates:
        if gate is not None:
            print(f"ID: {gate.id}, Type: {gate.type}, Qubit1: {gate.qubit1}, Qubit2: {gate.qubit2}, Theta: {gate.theta}")
        else:
            print("None")

def topological_sort(adj_mat):
    from collections import deque

    n = len(adj_mat)
    in_degree = [0] * n

    # Compute in-degrees
    for i in range(n):
        for j in range(n):
            if adj_mat[i][j] == 1:
                in_degree[j] += 1

    # Queue for nodes with in-degree 0
    queue = deque([i for i in range(n) if in_degree[i] == 0])
    topo_order = []

    while queue:
        node = queue.popleft()
        topo_order.append(node)

        for neighbor in range(n):
            if adj_mat[node][neighbor] == 1:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    if len(topo_order) != n:
        raise ValueError("Graph has a cycle! Topological sort not possible.")
    
    return topo_order


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
#     for gate in gates_schedule:
#         f.write(str(gate) + "\n")

np.set_printoptions(threshold=200, linewidth=200, precision=5, suppress=True)
    

print("Max difference:", np.max(np.abs(state - bench)))
print("Are they close?", np.allclose(state, bench, atol=1e-3))
print("Fidelity: ", np.abs(np.vdot(state, bench)))

diff_matrix = np.abs(state - bench)
max_diff_idx = np.unravel_index(np.argmax(diff_matrix), diff_matrix.shape)
print(f"Largest difference at index {max_diff_idx}:")
print(f"state: {state[max_diff_idx]}")
print(f"bench: {bench[max_diff_idx]}")

# remove redundant gates
gate_idx = 0
gate_lists_new = [[] for _ in range(n_qubits)]

for lst_idx, lst in enumerate(gate_lists):
    new_lst = []
    i = 0
    while i < len(lst):
        curr = lst[i]
        curr_type = curr.type
        curr_theta = curr.theta
        j = i + 1

        # Accumulate thetas for same-type gates
        while j < len(lst) and lst[j].type == curr_type:
            curr_theta += lst[j].theta
            j += 1

        # Only keep gate if total theta ≠ 0
        if curr_theta != 0:
            merged_gate = QGate.QGate(gate_idx, curr_type, curr.qubit1, curr.qubit2, curr_theta)
            gate_lists_new[lst_idx].append(merged_gate)
            gate_idx += 1

        i = j  # move to the next non-merged gate            

gate_lists = []

adj_mat = [[0 for __ in range(gate_idx)] for _ in range(gate_idx)]
gates = [None for _ in range(gate_idx)]
                    


# store hierarchy in QGate struct
for lst in gate_lists_new:
    for i in range(len(lst)):
        curr = lst[i]
        if i > 0:
            prev = lst[i - 1]
            adj_mat[prev.id][curr.id] = 1  # prev → curr
        if i < len(lst) - 1:
            next_ = lst[i + 1]
            adj_mat[curr.id][next_.id] = 1  # curr → next
        gates[curr.id] = curr

# iterate over the adjacency matrix to regain the states
for src_id in range(len(adj_mat)):
    for dst_id in range(len(adj_mat[src_id])):
        if adj_mat[src_id][dst_id] == 1:
            gates[src_id].next.append(gates[dst_id])
            gates[dst_id].prev.append(gates[src_id])

for gate in gates:
    if gate.type == "RY":
        print(len(gate.prev))

# print_adjacency_and_gates(adj_mat, gates)

order = topological_sort(adj_mat)
print("Topological order of gate IDs:", order)

gates_schedule = [[] for _ in range(0, len(gates))]

idx = 0
for i in order:
    gate = gates[i]
    if gate.type in ["RX", "RY"]:
        wires = [gate.qubit1]
    else:
        wires = [gate.qubit1, gate.qubit2]

    print((gate.type, gate.theta, wires))

    gates_schedule[idx].append((gate.type, gate.theta, wires))
    idx += 1

# print_gate_schedule(gates_schedule)

with open("qft_output.txt", "w") as f:
    for i in gates_schedule :
        f.write(str(i) + "\n")

graph = trap.create_trap_graph()
# router.router(gates, order, adj_mat, graph)

positions_history, gates_schedule = scheduler.scheduler(order, graph, gates)

with open("pos.txt", "w") as f:
    for k in positions_history:
        f.write(str(k))
        f.write("\n")
    
with open("schedule.txt", "w") as f:
    for k in gates_schedule:
        f.write(str(k))
        f.write("\n")


verifier.verifier(positions_history, gates_schedule, graph)


print("done")