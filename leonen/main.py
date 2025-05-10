from verifier import verifier
import generate_gate_sequence
from scheduler import schedule
import networkx as nx
import matplotlib.pyplot as plt
from custom_trap import create_trap_graph
from custom_trap import animate_positions_history


def main():
    # 1) Build trap
    trap = create_trap_graph()
    print("Trap graph created with", trap.number_of_nodes(), "nodes.")
    edges_with_attrs = list(trap.edges(data=True))


    # 2) Generate native gate sequence
    # sequence = generate_gate_sequence.get_qft_native_sequence(n_qubits=4)
    # print("Generated compiler_sequence with", len(sequence), "gates.")
    # print(sequence)

    # 3) Schedule positions and gates
    # positions_history, gates_schedule = schedule(trap, sequence)
    # print("Schedule computed:")
    # print("  • Time-steps:", len(positions_history))
    # print("  • Scheduled gate events:", sum(len(g) for g in gates_schedule))

    # Example Usage
    idle_height = 5 # update in custom_trap also if modified (there should be no reason to modify)
    SHOW_FRAME = False

    positions_history_advanced = [
    [(1, 0, 0), (0, 1, idle_height), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=0
    [(1, 0, 0), (0, 1, idle_height), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=1 RY1
    [(1, 0, 0), (0, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=2    RX1 D2
    [(1, 0, 0), (0, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=3    RY1 RY2
    [(1, 1, 0), (1, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=4    MV1 MV2
    [(1, 1, 0), (1, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=5    MS1 MS2
    [(1, 1, 0), (1, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=6    MS1 MS2
    [(1, 0, 0), (0, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=7    MV1 MV2
    [(1, 0, 0), (0, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=8    RX1
    [(1, 1, 0), (1, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=9    MV1 MV2
    [(1, 1, 0), (1, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=10    MS1 MS2
    [(1, 1, 0), (1, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=11    MS1 MS2
    [(1, 2, 0), (0, 1, 0), (0, 3, idle_height), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=12    MV1 MV2
    [(1, 2, 0), (0, 1, 0), (0, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=13    RY1 RY2 D3
    [(1, 2, 0), (0, 1, idle_height), (0, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=14    RY1 RY3 U2
    [(1, 3, 0), (0, 1, idle_height), (1, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=15    MV1 MV3
    [(1, 3, 0), (0, 1, idle_height), (1, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=16    MS1 MS3
    [(1, 3, 0), (0, 1, idle_height), (1, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=17    MS1 MS3
    [(1, 2, 0), (0, 1, idle_height), (0, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=18    MV1 MV3
    [(1, 2, 0), (0, 1, idle_height), (0, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=19    RX1
    [(1, 3, 0), (0, 1, idle_height), (1, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=20    MV1 MV3
    [(1, 3, 0), (0, 1, idle_height), (1, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=21    MS1 MS3
    [(1, 3, 0), (0, 1, idle_height), (1, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=22    MS1 MS3
    [(2, 3, 0), (0, 1, idle_height), (0, 3, 0), (1, 4, idle_height), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=23    MV1 MV3
    [(2, 3, 0), (0, 1, idle_height), (0, 3, 0), (1, 4, 0), (3, 4, idle_height), (4, 3, idle_height), (4, 1, idle_height), (3, 0, idle_height)],  # t=24  RY1 RY3 D4





]
    # position history (only two arguments)
    position_history = [[(x, y) for (x, y, z) in frame] for frame in positions_history_advanced]

    # 4) Verify correctness
    animate_positions_history(positions_history_advanced, SHOW_FRAME)

    # verifier(positions_history, gates_schedule, trap)

if __name__ == "__main__":
    main()





