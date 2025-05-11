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

class Ion:
    def __init__(self, node):
        self.node = node

i_node = (1,1)
i_node_p = (1,0)
i_node_n = (1,2)

def get_pos(ions):
    pos = []
    for ion in ions:
        pos.append(ion.node)
    return pos
        

def scheduler(order, graph, gates):
    positions_history = []
    gates_schedule = []
    time = 0

    ions = [
        Ion((0,0, "idle")),
        Ion((0,1, "idle")),
        Ion((0,2, "idle")),
        Ion((0,3, "idle")),
        Ion((0,4, "idle")),
        Ion((0,5, "idle")), 
        Ion((0,6, "idle")),
        Ion((1,6, "idle"))
            ]

    for i in order:
        gate = gates[i]
        print(gate.type)

        if gate.type in ["RX", "RY"]:
            ion = ions[gate.qubit1]
            x, y, z = ion.node
            ion.node = (x,y)
            positions_history.append(get_pos(ions))
            gates_schedule.append([])
            time +=1
            positions_history.append(get_pos(ions))
            gates_schedule.append([(str(gate.type), gate.theta, gate.qubit1)])
            time+=1
            ion.node = (x,y,z)
            positions_history.append(get_pos(ions))
            gates_schedule.append([])

        if gate.type == "MS":
            ion1 = ions[gate.qubit1]
            ion2 = ions[gate.qubit2]
            x1, y1, z1 = ion1.node
            x2, y2, z2 = ion2.node

            path1 = nx.shortest_path(graph, source=ion1.node, target=i_node_p)
            path2 = nx.shortest_path(graph, source=ion2.node, target=i_node_n)

            for t in range(len(path1)):
                node = path1[t]
                ion1.node = node
                positions_history.append(get_pos(ions))
                gates_schedule.append([])
                time += 1

            for t in range(len(path2)):
                node = path2[t]
                ion2.node = node
                positions_history.append(get_pos(ions))
                gates_schedule.append([])
                time += 1

            ion1.node = i_node
            ion2.node = i_node
            positions_history.append(get_pos(ions))
            gates_schedule.append([])
            time += 1
            positions_history.append(get_pos(ions))
            gates_schedule.append([(str(gate.type), gate.theta, [gate.qubit1, gate.qubit2])])
            # time += 1
            # positions_history.append(get_pos(ions))
            # gates_schedule.append([])
            time += 1
            ion1.node = i_node_p
            ion2.node = i_node_n
            positions_history.append(get_pos(ions))
            gates_schedule.append([])
            time += 1

            path1 = []
            path2 = []

            path1 = nx.shortest_path(graph, source=i_node_p, target=(x1, y1, z1))
            path2 = nx.shortest_path(graph, source=i_node_n, target=(x2, y2, z2))

            for t in range(len(path1)):
                node = path1[t]
                ion1.node = node
                positions_history.append(get_pos(ions))
                gates_schedule.append([])
                time += 1

            for t in range(len(path2)):
                node = path2[t]
                ion2.node = node
                positions_history.append(get_pos(ions))
                gates_schedule.append([])
                time += 1

    return [positions_history, gates_schedule]