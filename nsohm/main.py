# main.py

from trap import create_trap_graph
from verifier import verifier
import generate_gate_sequence
from scheduler import naive_schedule

def main():
    # 1) Build trap & native sequence
    trap = create_trap_graph()
    print("Trap graph created with", trap.number_of_nodes(), "nodes.")

    compiler_sequence = generate_gate_sequence.get_qft_native_sequence(n_qubits=8)
    print("Generated compiler_sequence with", len(compiler_sequence), "gates.")

    # 2) Generate the naive but valid schedule
    positions_history, gates_schedule = naive_schedule(trap, compiler_sequence)
    print("Schedule computed:")
    print("  • Time-steps:", len(positions_history))
    total_gates = sum(len(step) for step in gates_schedule)
    print("  • Total gate-executions:", total_gates)

    # 3) (Re-)enable verification to check constraints
    print("Verifying schedule...")
    verifier(positions_history, gates_schedule, trap)
    print("✅ Verification passed.")

    # 4) Optionally show the first few steps
    print("\nFirst 5 time‐steps:")
    for t in range(min(5, len(positions_history))):
        print(f" t={t:2d}", positions_history[t], "gates:", gates_schedule[t])

if __name__ == "__main__":
    main()
