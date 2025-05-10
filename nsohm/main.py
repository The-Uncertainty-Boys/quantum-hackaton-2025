from trap import create_trap_graph
from verifier import verifier
import generate_gate_sequence
from scheduler import schedule

def main():
    # 1) Build trap
    trap = create_trap_graph()
    print("Trap graph created with", trap.number_of_nodes(), "nodes.")

    # 2) Generate native gate sequence
    sequence = generate_gate_sequence.get_qft_native_sequence(n_qubits=8)
    print("Generated compiler_sequence with", len(sequence), "gates.")

    # 3) Schedule positions and gates
    positions_history, gates_schedule = schedule(trap, sequence)
    print("Schedule computed:")
    print("  • Time-steps:", len(positions_history))
    print("  • Scheduled gate events:", sum(len(g) for g in gates_schedule))

    # 4) Verify correctness
    verifier(positions_history, gates_schedule, trap)

if __name__ == "__main__":
    main()