import networkx as nx

def schedule(trap, sequence, initial_positions=None):
    """
    Schedule a list of native gates on the Penning trap.

    Args:
        trap: networkx.Graph with node attribute 'type' in {'standard','interaction','idle'}.
        sequence: List of gates as tuples, e.g. ("RX", angle, q) or ("MS", angle, c, t).
        initial_positions: Optional list of 8 node IDs for the starting positions.

    Returns:
        positions_history: List of length T of ion-position lists (length 8).
        gates_schedule:   List of length T of gate lists executed at each timestep.
    """
    # Determine initial positions
    if initial_positions is None:
        std_nodes = [n for n, d in trap.nodes(data=True) if d['type'] == 'standard']
        initial_positions = std_nodes[:8]

    positions_history = [list(initial_positions)]
    gates_schedule = [[]]
    current = list(initial_positions)

    # Precompute node sets
    standard_nodes = [n for n, d in trap.nodes(data=True) if d['type'] == 'standard']
    interaction_nodes = [n for n, d in trap.nodes(data=True) if d['type'] == 'interaction']

    def append_step(moves, gates):
        # apply moves
        for ion, node in moves:
            current[ion] = node
        positions_history.append(list(current))
        gates_schedule.append(list(gates))

    for gate in sequence:
        name = gate[0]
        if name in ('RX', 'RY'):
            _, angle, q = gate
            # Move ion to a standard node if not already
            if trap.nodes[current[q]]['type'] != 'standard':
                dists = {n: nx.shortest_path_length(trap, current[q], n) for n in standard_nodes}
                target = min(dists, key=dists.get)
                path = nx.shortest_path(trap, current[q], target)
                for step in path[1:]:
                    append_step([(q, step)], [])
            # Execute RX/RY gate
            append_step([], [(name, angle, q)])

        elif name == 'MS':
            _, angle, c, t = gate
            # Find best interaction node by sum of distances
            best_node = min(
                interaction_nodes,
                key=lambda inode: (nx.shortest_path_length(trap, current[c], inode)
                                   + nx.shortest_path_length(trap, current[t], inode))
            )
            # Shuttle ions to that node
            for ion, path in ((c, nx.shortest_path(trap, current[c], best_node)),
                              (t, nx.shortest_path(trap, current[t], best_node))):
                for step in path[1:]:
                    append_step([(ion, step)], [])
            # Apply MS gate start
            append_step([], [("MS", angle, (c, t))])
            # Second timestep of MS (stationary)
            append_step([], [])
            # Move ions off interaction node to nearest standard neighbors
            neighbors = [n for n in trap.neighbors(best_node) if trap.nodes[n]['type'] == 'standard']
            off_c = neighbors[0]
            off_t = neighbors[1] if len(neighbors) > 1 else neighbors[0]
            append_step([(c, off_c), (t, off_t)], [])

        else:
            raise ValueError(f"Unknown gate type: {gate}")

    return positions_history, gates_schedule
