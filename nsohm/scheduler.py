import networkx as nx
from ortools.sat.python import cp_model

def schedule(trap: nx.Graph, sequence: list) -> tuple:
    num_ions = 8  # number of qubits/ions
    nodes = list(trap.nodes())
    node_index = {node: idx for idx, node in enumerate(nodes)}
    # Upper bound on time horizon (e.g., 2 * number of gates as a rough bound)
    horizon = len(sequence) * 2  
    horizon = 10

    model = cp_model.CpModel()
    # Position variables: x[i,n,t] = 1 if ion i at node n at time t
    x = {}
    for i in range(num_ions):
        for n in nodes:
            for t in range(horizon + 1):
                x[(i, n, t)] = model.NewBoolVar(f"x_{i}_{node_index[n]}_{t}")

    # Gate start variables for single-qubit gates
    gstart_single = {}
    # Gate start variables for two-qubit gates (MS/CP)
    gstart_two = {}
    # Duration and involved qubits for each gate
    gate_duration = {}
    gate_qubits = {}

    # Declare gate start vars based on gate type
    for g_idx, gate in enumerate(sequence):
        op = gate[0]
        if op == "CP" or op == "MS":
            # Two-qubit controlled-phase gate (treated as MS two-qubit gate)
            _, angle, q1, q2 = gate  # gate format ("CP", angle, ctrl, targ)
            gate_duration[g_idx] = 2  # two-qubit gate takes 2 time units
            gate_qubits[g_idx] = (q1, q2)
            # Create start var for each interaction node and time
            for t in range(horizon):
                for n in nodes:
                    if trap.nodes[n]['type'] == 'interaction':
                        gstart_two[(g_idx, n, t)] = model.NewBoolVar(f"g2_{g_idx}_{node_index[n]}_{t}")
        else:
            # Single-qubit rotation (RX, RY, RZ, or H)
            if op == "H":
                # Hadamard (treat as RY or RX type single-qubit gate with 1 step)
                _, q = gate
                q_index = q
            else:
                # e.g. ("RX", angle, q)
                _, angle, q = gate
                q_index = q
            gate_duration[g_idx] = 1  # single-qubit gate takes 1 time unit
            gate_qubits[g_idx] = (q_index,)
            # Create start var for each time
            for t in range(horizon):
                gstart_single[(g_idx, t)] = model.NewBoolVar(f"g1_{g_idx}_{t}")

    ## Constraint 1: Each ion occupies exactly one node per timestep
    for t in range(horizon + 1):
        for i in range(num_ions):
            model.Add(sum(x[(i, n, t)] for n in nodes) == 1)
    # Also ensure each node has at most capacity per timestep (covered in Constraint 3 below).

    ## Constraint 2: Ions move only to adjacent nodes (or stay)
    for i in range(num_ions):
        for t in range(horizon):
            for n in nodes:
                for m in nodes:
                    if m != n and m not in trap[n]:  # if no direct edge between n and m
                        # Cannot move from n at t to m at t+1 if not neighbors
                        model.Add(x[(i, n, t)] + x[(i, m, t+1)] <= 1)

    ## Constraint 3: Node capacity constraints 
    for t in range(horizon + 1):
        for n in nodes:
            node_type = trap.nodes[n]['type']
            if node_type in {"standard", "idle"}:
                # Standard/idle: at most 1 ion
                model.Add(sum(x[(i, n, t)] for i in range(num_ions)) <= 1)
            elif node_type == "interaction":
                # Interaction: at most 2 ions, and if 2 ions are present, an MS gate must be starting
                model.Add(sum(x[(i, n, t)] for i in range(num_ions)) <= 
                          1 + sum(gstart_two[(g_idx, n, t)] 
                                  for g_idx in range(len(sequence)) 
                                  if (g_idx, n, t) in gstart_two))
    # Gate locality: ensure single-qubit gates only on standard nodes, two-qubit only on interaction nodes
    for (g_idx, t), var in gstart_single.items():
        q = gate_qubits[g_idx][0]
        # If gate g starts at t, the qubit must be on some standard node at t
        model.Add(sum(x[(q, n, t)] for n in nodes if trap.nodes[n]['type'] == 'standard') >= var)
    for (g_idx, n, t), var in gstart_two.items():
        q1, q2 = gate_qubits[g_idx]
        # If two-qubit gate g starts at node n at time t, both qubits must be there at t (and t+1, enforced below)
        model.Add(x[(q1, n, t)] >= var)
        model.Add(x[(q2, n, t)] >= var)
        model.Add(x[(q1, n, t+1)] >= var)
        model.Add(x[(q2, n, t+1)] >= var)

    ## Constraint 4: Gate start and duration constraints
    # Each gate must start exactly once.
    for g_idx in range(len(sequence)):
        if len(gate_qubits[g_idx]) == 1:
            model.Add(sum(gstart_single[(g_idx, t)] for t in range(horizon)) == 1)
        else:
            model.Add(sum(gstart_two[(g_idx, n, t)] 
                          for n in nodes if trap.nodes[n]['type'] == 'interaction' 
                          for t in range(horizon)) == 1)
    # (By linking positions as above, two-qubit gates occupy two timesteps of those qubits.)

    ## Constraint 5: Gate dependency (ordering on same qubits)
    for g1 in range(len(sequence)):
        for g2 in range(g1 + 1, len(sequence)):
            # If gate g1 and g2 act on a common qubit, enforce order g1 before g2
            if set(gate_qubits[g1]) & set(gate_qubits[g2]):  # they share at least one qubit
                # g1 comes before g2 in the sequence list, so g2 cannot start before g1 is done
                # Let dur1 = gate_duration[g1]
                dur1 = gate_duration[g1]
                # For every possible start times t1 for g1 and t2 for g2 that violate order (t2 < t1+dur1):
                for t1 in range(horizon):
                    for t2 in range(t1 + dur1):
                        if t2 < horizon:
                            if len(gate_qubits[g1]) == 1:
                                # g1 is single-qubit
                                model.Add(gstart_single[(g1, t1)] + (
                                          gstart_single[(g2, t2)] if len(gate_qubits[g2]) == 1 
                                          else sum(gstart_two[(g2, n, t2)] for n in nodes if (g2, n, t2) in gstart_two)
                                         ) <= 1)
                            else:
                                # g1 is two-qubit
                                model.Add(sum(gstart_two[(g1, n, t1)] for n in nodes if (g1, n, t1) in gstart_two) + (
                                          gstart_single[(g2, t2)] if len(gate_qubits[g2]) == 1 
                                          else sum(gstart_two[(g2, n, t2)] for n in nodes if (g2, n, t2) in gstart_two)
                                         ) <= 1)

    ## Constraint 6: No simultaneous edge swap (no crossing paths)
    for t in range(horizon):
        for (u, v) in trap.edges():
            for i in range(num_ions):
                for j in range(i + 1, num_ions):
                    # Prevent ion i at u and j at v at time t from swapping to v and u at t+1
                    model.Add(x[(i, u, t)] + x[(j, v, t)] + x[(i, v, t+1)] + x[(j, u, t+1)] <= 3)

    ## Objective: minimize makespan (total schedule length)
    makespan = model.NewIntVar(0, horizon, "makespan")
    # Link makespan to gate end times:
    for (g_idx, t), var in gstart_single.items():
        # if gate g_idx (duration 1) starts at t, then makespan >= t
        model.Add(makespan >= t).OnlyEnforceIf(var)
    for (g_idx, n, t), var in gstart_two.items():
        # if gate g_idx (duration 2) starts at t, makespan >= t+1
        model.Add(makespan >= t + gate_duration[g_idx] - 1).OnlyEnforceIf(var)
    model.Minimize(makespan)

    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30  # limit solver time if needed
    solver.parameters.num_search_workers = 8    # parallel threads
    result = solver.Solve(model)
    if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible schedule found for the given circuit.")

    # Extract the schedule
    T = solver.Value(makespan)
    positions_history = []
    gates_schedule = []
    for t in range(T + 1):
        # gather positions of all 8 ions at time t
        positions = []
        for i in range(num_ions):
            for n in nodes:
                if solver.Value(x[(i, n, t)]) == 1:
                    # append the coordinate (row,col) or (row,col,'idle') of node
                    positions.append(n)
                    break
        positions_history.append(positions)
        # gather all gates starting at time t
        timestep_gates = []
        for g_idx, gate in enumerate(sequence):
            if gate_duration[g_idx] == 1:
                # single-qubit gate
                if any(solver.Value(gstart_single[(g_idx, t0)]) == 1 for t0 in [t] if (g_idx, t0) in gstart_single):
                    op = gate[0]
                    if op == "H":
                        _, q = gate
                        timestep_gates.append(("H", q))
                    else:
                        _, angle, q = gate
                        timestep_gates.append((op, angle, q))
            else:
                # two-qubit gate (MS/CP)
                for n in nodes:
                    if (g_idx, n, t) in gstart_two and solver.Value(gstart_two[(g_idx, n, t)]) == 1:
                        _, angle, q1, q2 = gate
                        timestep_gates.append(("MS", angle, (q1, q2)))
                        break  # one start per gate
        gates_schedule.append(timestep_gates)
    return positions_history, gates_schedule
