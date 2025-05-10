# scheduler.py

import networkx as nx
from networkx.exception import NetworkXNoPath

def naive_schedule(graph, gate_sequence):
    """
    A naive, valid schedule:
      - All 8 ions have fixed 'homes' on row 4 and ion 0 on (0,0).
      - Every MS gate uses a fixed interaction node (1,1).
      - Ions move one at a time to that node and back.
      - Single-qubit gates happen at home.
    Returns (positions_history, gates_schedule).
    """
    # Define homes: ion 0 at (0,0); ions 1–7 on row 4 columns 0–6
    homes = {
        0: (0, 0),
        1: (4, 0),
        2: (4, 1),
        3: (4, 2),
        4: (4, 3),
        5: (4, 4),
        6: (4, 5),
        7: (4, 6),
    }
    # Fixed interaction node
    interact = (1, 1)

    positions_history = []
    gates_schedule    = []

    def snapshot(step_gates):
        # snapshot current positions of ions [0..7]
        positions_history.append([homes[i] if i not in moving else pos[i]
                                  for i in range(8)])
        gates_schedule.append(step_gates)

    # current in-transit positions for the one moving ion
    pos = homes.copy()

    for gate in gate_sequence:
        name = gate[0]
        if name in ("RX", "RY"):
            # single-qubit at home
            snapshot([gate])
            continue

        # MS gate
        _, φ, i, j = gate
        moving = {}

        # Move ion i to interaction
        path_i = nx.shortest_path(graph, homes[i], interact)
        for node in path_i[1:]:
            pos[i] = node
            moving[i] = True
            snapshot([])  # no gate while moving
        # Move ion j
        path_j = nx.shortest_path(graph, homes[j], interact)
        for node in path_j[1:]:
            pos[j] = node
            moving[j] = True
            snapshot([])

        # Now both i,j at interact: execute MS
        snapshot([gate])

        # Move j back
        for node in reversed(path_j[:-1]):
            pos[j] = node
            moving[j] = True
            snapshot([])
        # Move i back
        for node in reversed(path_i[:-1]):
            pos[i] = node
            moving[i] = True
            snapshot([])

        # Reset moving tracking
        moving.clear()
        # Reset pos to homes so that all ions again at homes
        pos = homes.copy()

    return positions_history, gates_schedule
