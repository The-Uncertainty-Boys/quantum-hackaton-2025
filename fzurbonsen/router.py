import sys
import os
import networkx as nx
import matplotlib.pyplot as plt
import pennylane as qml
from pennylane import numpy as np

import QGate
import Qubit

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import trap  # Import trap module

max_ms_gates = 1

# function to update the positions history by checking the position of all qubits
def update_pos_history(positions_history, qubits):
    pos = []
    for qubit in qubits:
        if qubit.idle:
            i, j = qubit.node
            pos.append((i, j, "idle"))
        else:
            pos.append(qubit.node)
    positions_history.append(pos)
    return positions_history

def print_status(gates, next_gates, active_gates):
    print("gates:")
    for gate in gates:
        print(str(gate))
    print("next_gates:")
    for gate in next_gates:
        print(str(gate))
    print("active_gates:")
    for gate in active_gates:
        print(str(gate))
    print("\n")

# function to create a mapping
def router(gates, order, adj_mat, graph):
    pos = []
    qubits = []
    positions_history = []
    active_qubits = []
    next_gates = []
    active_gates = []

    print_status(gates, next_gates, active_gates)

    for i in range(1):
        next_gates.append(gates[order[i]])
        gates.remove(gates[order[i]])

    print_status(gates, next_gates, active_gates)

    curr_node = (0,0)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    # curr_node = (0,1)
    # qubits.append(Qubit.Qubit(curr_node, graph))
    # pos.append(curr_node)
    # curr_node = (1,1)
    # qubits.append(Qubit.Qubit(curr_node, graph))
    # pos.append(curr_node)
    update_pos_history(positions_history, qubits)

    time_step = 0

    active_ms_gates = 0
    while len(active_gates) > 0 or len(next_gates) > 0 or len(gates) > 0:
        # while we have not reached the threshold for ms gates we try to pull more gates
        while active_ms_gates < max_ms_gates and len(next_gates) > 0:
            active_gates.append(next_gates[0])
            if next_gates[0].type == "MS":
                active_ms_gates += 1
            next_gates.pop(0)
        
        # process the active gates
        while len(active_gates) > 0:
            
            time_step += 1





    
    print(positions_history)





graph = trap.create_trap_graph()
gates = []
order = []
adj_mat = []

gates.append(QGate.QGate(0, "RX", 0))
order.append(0)

router(gates, order, adj_mat, graph)