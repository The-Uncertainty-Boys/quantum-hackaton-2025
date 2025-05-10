import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from matplotlib.animation import FuncAnimation
from PIL import Image
import glob
import os

# Ensure the directory exists
os.makedirs('img', exist_ok=True)

# Option to show frames or not show them
SHOW_FRAME = False

idle_height = 5


def create_trap_graph() -> nx.Graph:
    """Create a graph representing the Penning trap.

    The Penning trap is represented as a grid of nodes, where each node can be
    either an interaction node or a standard node. The interaction nodes are
    connected to their corresponding idle nodes, and the standard nodes are
    connected to their neighboring standard nodes.
    """

    trap = nx.Graph()

    rows = 5
    cols = 7

    interaction_nodes = [(1, 1), (1, 3), (3, 1), (3, 3), (1, 5), (3, 5)]


    for r in range(rows):
        for c in range(cols):
            base_node_id = (r, c)

            if base_node_id in interaction_nodes:
                trap.add_node(base_node_id, type="interaction", color="red", xyz=[r,c,0], cost=0.02)
            else:
                trap.add_node(base_node_id, type="standard", color="blue",xyz=[r,c,0], cost=0.02)
                rest_node_id = (r, c, "idle")
                trap.add_node(rest_node_id, type="idle", color="green", xyz=[r,c,idle_height], cost=0.01)
                trap.add_edge(base_node_id, rest_node_id, cost=0.03)

    for r in range(rows):
        for c in range(cols):
            node_id = (r, c)
            if c + 1 < cols:
                neighbor_id = (r, c + 1)
                trap.add_edge(node_id, neighbor_id, cost=0.03)
            if r + 1 < rows:
                neighbor_id = (r + 1, c)
                trap.add_edge(node_id, neighbor_id, cost=0.03)

    return trap

# create graph
trap = create_trap_graph()


# Extract node positions and colors
pos = {node: data['xyz'] for node, data in trap.nodes(data=True)}
colors = [data['color'] for node, data in trap.nodes(data=True)]

# Example Usage
positions_history_advanced = [
    [(1, 0, 0), (0, 1, idle_height), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # Initial positions at t=0
    [(1, 0, 0), (0, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # Initial positions at t=1
    [(1, 0, 0), (0, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # Initial positions at t=2
    [(1, 1, 0), (1, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # Initial positions at t=3
]


# DRAW the current state of the Penning Trap
def draw_current_state(last_state, list_nr, show_frame):


    # initialize figure
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Draw nodes
    for node, (x, y, z) in pos.items():
        color = trap.nodes[node]['color']
        ax.scatter(x, y, z, c=color, s=80, edgecolors='k')


    # Draw edges
    for u, v in trap.edges():
        x = [pos[u][0], pos[v][0]]
        y = [pos[u][1], pos[v][1]]
        z = [pos[u][2], pos[v][2]]
        ax.plot(x, y, z, color='gray', alpha=0.6)

    # count how many qubits are on the same node
    counts = Counter(last_state)
    for qubit_pos, count in counts.items():
        pos_values = [tuple(v) for v in pos.values()]
        if qubit_pos in pos_values:
            x, y, z = qubit_pos
            if count == 1:
                # plot single qubits
                ax.scatter(x, y, z, c='yellow', s=200, marker='*', edgecolors='k', label='1 Qubit')
            else:
                # plot double qubits
                ax.scatter(x, y, z, c='magenta', s=300, marker='*', edgecolors='k', label='2 Qubits')
        else:
            # Handle idle nodes if needed
            print("Error: position might be invalid")
            pass
        


    # Only show one legend entry for each type
    handles, labels = ax.get_legend_handles_labels()
    seen = set()
    unique_handles = []
    unique_labels = []
    for h, l in zip(handles, labels):
        if l not in seen:
            unique_handles.append(h)
            unique_labels.append(l)
            seen.add(l)
    if unique_handles:
        ax.legend(unique_handles, unique_labels)

    # x and y label
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    # Hide the z-axis
    ax.set_zticks([])  # Remove z-axis ticks
    ax.set_zticklabels([])  # Remove z-axis tick labels
    ax.set_zlabel('')  # Remove z-axis label

    ax.set_xticks(np.arange(0, 5, 1))  # For columns 0 to 6 (change 7 if your grid size changes)

    plt.title("Penning Trap Graph (3D)")
    plt.tight_layout()
    plt.savefig('img/foo' + str(list_nr)+'.png')

    if (show_frame):
        plt.show()

# example usage for only one frame
draw_current_state(positions_history_advanced[-1], len(positions_history_advanced)-1, SHOW_FRAME, )


def animate_positions_history(positions_history, show_frames):
    for i in range(0, len(positions_history)):
        draw_current_state(positions_history[i], i, show_frames)


    # Create the frames
    frames = []
    imgs = sorted(glob.glob("img/*.png"))
    for i in imgs:
        print(i)
        new_frame = Image.open(i)
        frames.append(new_frame)

    # Save into a GIF file that loops forever
    frames[0].save('img/png_to_gif.gif', format='GIF',
                append_images=frames[1:],
                save_all=True,
                duration=1200, loop=0)


# example usage for whole animation
animate_positions_history(positions_history_advanced, SHOW_FRAME)
