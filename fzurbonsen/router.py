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
interaction_nodes = [(1, 1), (1, 3), (3, 1), (3, 3), (1, 5), (3, 5)]

# function to add a gate to the schedule
def push_to_schedule(gate_type, param, wires, gates_schedule, time_step):

    while len(gates_schedule) <= time_step:
        gates_schedule.append([])  # Ensure enough time slots
    gates_schedule[time_step].append((gate_type, param, wires))
    return gates_schedule

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

def print_status(gates, next_gates, active_gates, finished_gates):
    print("gates:")
    for gate in gates:
        print(str(gate))
    print("next_gates:")
    for gate in next_gates:
        print(str(gate))
    print("active_gates:")
    for gate in active_gates:
        print(str(gate))
    print("finished_gates:")
    for gate in finished_gates:
        print(str(gate))
    print("\n")

# function to create a mapping
def router(gates, order, adj_mat, graph):

    pos = []
    qubits = []
    positions_history = []
    gates_schedule = []
    active_qubits = []
    to_idle = []
    next_gates = []
    active_gates = []
    finished_gates = []
    processed_gates = []
    free_interaction_nodes = interaction_nodes

    # print_status(gates, next_gates, active_gates)

    order_set = set()

    i = 0
    while True:
        gate = gates[order[i]]
        if gate.type in ["RX", "RY"]:
            if gate.qubit1 not in order_set:
                next_gates.append(gate)
                order_set.add(gate.qubit1)
                i += 1
            else:
                break
        else:
            if (gate.qubit1 not in order_set) and (gate.qubit2 not in order_set):
                next_gates.append(gate)
                order_set.add(gate.qubit1)
                order_set.add(gate.qubit2)
                i += 1
        

    for gate in next_gates:
        gates.remove(gate)
        order.pop(0)


    # print_status(gates, next_gates, active_gates)


    curr_node = (0,0)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    curr_node = (0,1)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    curr_node = (0,2)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    curr_node = (0,4)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    curr_node = (0,5)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    curr_node = (0,6)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    curr_node = (1,6)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    curr_node = (2,6)
    qubits.append(Qubit.Qubit(curr_node, graph))
    pos.append(curr_node)
    update_pos_history(positions_history, qubits)

    time_step = 0

    with open("output.log", "w") as f:
        f.write("outuput.log\n")

    active_ms_gates = 0
    while len(active_gates) > 0 or len(next_gates) > 0:
        finished_gates = []

    
        # while we have not reached the threshold for ms gates we try to pull more gates
        while active_ms_gates < max_ms_gates and len(next_gates) > 0:
            active_gates.append(next_gates[0])
            if next_gates[0].type == "MS":
                active_ms_gates += 1
            next_gates.pop(0)

        with open("output.log", "a") as f:
            f.write("\n\n")
            f.write("\n\n")
            f.write("gates:")
            for gate in gates:
                f.write(str(gate)+"\n")
            f.write("\n")
            f.write("next_gates:")
            for gate in next_gates:
                f.write(str(gate)+"\n")
            f.write("\n")
            f.write("active_gates:")
            for gate in active_gates:
                f.write(str(gate)+"\n")
            f.write("\n\n")


        # print_status(gates, next_gates, active_gates)
        # print(len(gates))
        
        # process the active gates
        while len(active_gates) > 0:

            with open("output.log", "a") as f:
                f.write("\n\n")
                f.write("\n\n")
                f.write("gates:")
                for gate in gates:
                    f.write(str(gate)+"\n")
                f.write("\n")
                f.write("next_gates:")
                for gate in next_gates:
                    f.write(str(gate)+"\n")
                f.write("\n")
                f.write("active_gates:")
                for gate in active_gates:
                    f.write(str(gate)+"\n")
                f.write("\n\n")
            
            # iterate over all active gates
            for qubit in qubits:
                qubit.free = 1
            tmp_gates = active_gates
            for gate in tmp_gates:

                # we first check the RX and RY gates
                if gate.type in ["RX", "RY"]:
                    qubit = qubits[gate.qubit1]

                    # if the qubit is not yet processing we try to activate it
                    if qubit.processing == 0:
                        # qubit was idle and will be activated
                        if qubit.idle == 1:
                            new_pos = qubit.set_active(pos)
                            if new_pos:
                                pos = new_pos
                                qubit.processing = 1
                                active_qubits.append(qubit)

                        # qubit wasn't idle and can be continued to be used
                        else:
                            # check if the qubit is on an interactive field
                            if qubit.node in interaction_nodes:
                                # move the qubit
                                new_pos = qubit.move_to_free(pos)
                                if new_pos:
                                    pos = new_pos
                                qubit.processing = 1
                            else:
                                # perform the quantum operation
                                push_to_schedule(gate.type, gate.theta, gate.qubit1, gates_schedule, time_step)
                                # remove the gate from active gates
                                active_gates.remove(gate)
                                finished_gates.append(gate)
                                # add qubit to the qubits to be idled
                                to_idle.append(qubit)
                                qubit.processing = 0

                    else:
                        # check if we are on an interaction node
                        if qubit.node in interaction_nodes:
                            # move the qubit
                            new_pos = qubit.move_to_free(pos)
                            if new_pos:
                                pos = new_pos
                            qubit.processing = 1
                        else:
                            # perform the quantum operation
                            push_to_schedule(gate.type, gate.theta, gate.qubit1, gates_schedule, time_step)
                            # remove the gate from active gates
                            active_gates.remove(gate)
                            finished_gates.append(gate)
                            # add qubit to the qubits to be idled
                            to_idle.append(qubit)
                            qubit.processing = 0



                # if the gate is a MS gate
                elif gate.type == "MS":
                    qubit1 = qubits[gate.qubit1]
                    qubit2 = qubits[gate.qubit2]


                    # check if the qubit is processing
                    if qubit1.processing == 0 and qubit2.processing == 0:
                        # aquire an interaction node
                        interaction_node = qubit1.find_next_free_interaction_node(free_interaction_nodes)
                        free_interaction_nodes.remove(interaction_node)

                        # find paths to the interaction nodes
                        path1 = qubit1.find_path(interaction_node)
                        path2 = qubit2.find_path(interaction_node)
                        qubit1.set_path(path1)
                        qubit2.set_path(path2)
                        
                        # by setting the path we have started the processing therefore the field needs to be updated
                        qubit1.processing = 1
                        qubit2.processing = 1

                        # check if the qubit1 is idle
                        if qubit1.idle == 1:
                            new_pos = qubit1.set_active(pos)
                            if new_pos != None:
                                pos = new_pos
                                active_qubits.append(qubit1)
                        else:
                            # move to the next step in the path
                            new_pos = qubit1.try_next_move(pos)
                            if new_pos != None:
                                pos = new_pos

                        # check if the qubit2 is idle
                        if qubit2.idle == 1:
                            new_pos = qubit2.set_active(pos)
                            if new_pos != None:
                                pos = new_pos
                                active_qubits.append(qubit2)
                        else:
                            # move to the next step in the path
                            new_pos = qubit2.try_next_move(pos)
                            if new_pos != None:
                                pos = new_pos

                    # if the process has already been started
                    elif qubit1.processing == 1 and qubit2.processing == 1:

                        # check if the qubit1 is idle
                        if qubit1.idle == 1:
                            new_pos = qubit1.set_active(pos)
                            if new_pos != None:
                                pos = new_pos
                                active_qubits.append(qubit1)
                        else:
                            # move to the next step in the path
                            new_pos = qubit1.try_next_move(pos)
                            if new_pos != None:
                                pos = new_pos

                        # check if the qubit2 is idle
                        if qubit2.idle == 1:
                            new_pos = qubit2.set_active(pos)
                            if new_pos != None:
                                pos = new_pos
                                active_qubits.append(qubit2)
                        else:
                            # move to the next step in the path
                            new_pos = qubit2.try_next_move(pos)
                            if new_pos != None:
                                pos = new_pos

                        # check if the two qubits have arived
                        if len(qubit1.path) == 0 and len(qubit2.path) == 0:
                            if (qubit1.node != qubit2.node):
                                raise AssertionError("nodes do not match for two qubits in a MS gate")

                            # check if they have can perform an action in this turn
                            if qubit1.free == 1 and qubit2.free == 1:
                                # check if this is the first or the second time step the gate is performed
                                if gate.time_index == 0:
                                    # we perform and log the gate
                                    push_to_schedule(gate.type, gate.theta, [gate.qubit1, gate.qubit2], gates_schedule, time_step)
                                else:
                                    # the gate is finished so we can wrap up
                                    active_gates.remove(gate)
                                    finished_gates.append(gate)
                                    # push the qubits to idle
                                    to_idle.append(qubit1)
                                    to_idle.append(qubit2)
                                    qubit1.processing = 0
                                    qubit2.processing = 0
                                    # return free interaction node
                                    free_interaction_nodes.append(qubit1.node)
                                gate.time_index += 1
                    else:
                        raise AssertionError("error not both qubits are processing in an MS gate")
                else:
                    raise AssertionError("error: unknown gate")

        # take care of qubits that are sent to idle
        active_qubits = []
        for gate in active_gates:
            if gate.type in ["RX", "RY"]:
                active_qubits.append(gate.qubit1)
            else:
                active_qubits.append(gate.qubit1)
                active_qubits.append(gate.qubit1)

        for i in range(len(qubits)):
            if i not in active_qubits:
                qubits[i].set_idle(pos)

        for qubit in qubits:
            if qubit.processing == 0:
                new_pos = qubit.set_idle(pos)
                pos = new_pos

        for qubit in to_idle:
            new_pos = qubit.set_idle(pos)
            if new_pos != None:
                pos = new_pos

        update_pos_history(positions_history, qubits)
        for qubit in qubits:
            qubit.next_tick()

        # prepare for next iteration  
        print_status(gates, next_gates, active_gates, finished_gates)
        # fetch new next gates
        # for gate in finished_gates:
        #     if gate.type in ["RX", "RY"]:
        #         n_g = gate.next[0]
        #         if n_g in gates:
        #             with open("output.log", "a") as f:
        #                 f.write(str(gate.next)+"\n")
        #             if n_g.type in ["RX", "RY"]:
        #                 next_gates.append(n_g)
        #                 gates.remove(n_g)
        #             else:
        #                 print(n_g.id)
        #                 print(len(n_g.next))
        #                 if (n_g.prev[0] in processed_gates or n_g.prev[0] in finished_gates) and \
        #                     (n_g.prev[1] in processed_gates or n_g.prev[1] in finished_gates):
        #                     next_gates.append(n_g)
        #                     gates.remove(n_g)
        #     else:
        #         for n_g in gate.next:
        #             if n_g in gates:
        #                 if n_g.type in ["RX", "RY"]:
        #                     next_gates.append(n_g)
        #                     gates.remove(n_g)
        #                 else:
        #                     if (n_g.prev[0] in processed_gates or n_g.prev[0] in finished_gates) and \
        #                         (n_g.prev[1] in processed_gates or n_g.prev[1] in finished_gates):
        #                         next_gates.append(n_g)
        #                         gates.remove(n_g)
        #     processed_gates.append(gate)

        order_set = set()

        i = 0
        while True:
            gate = gates[order[i]]
            if gate.type in ["RX", "RY"]:
                if gate.qubit1 not in order_set:
                    next_gates.append(gate)
                    order_set.add(gate.qubit1)
                    i += 1
                else:
                    break
            else:
                if (gate.qubit1 not in order_set) and (gate.qubit2 not in order_set):
                    next_gates.append(gate)
                    order_set.add(gate.qubit1)
                    order_set.add(gate.qubit2)
                    i += 1
            

        for gate in next_gates:
            gates.remove(gate)
            order.pop(0)

        print(len(order))
                    

        finished_gates = []
        time_step += 1





    print(positions_history)
    print(gates_schedule)





# graph = trap.create_trap_graph()
# gates = []
# order = []
# adj_mat = []

# gates.append(QGate.QGate(0, "RX", 0))
# gates.append(QGate.QGate(1, "RX", 1))
# gates.append(QGate.QGate(2, "MS", 0, 1))
# order.append(0)
# order.append(1)

# print(str(gates[0]))
# print(str(gates[1]))
# print(str(gates[2]))
# print(order)


# gates[0].next = gates[2]
# gates[1].next = gates[2]

# gates[2].prev = [gates[0], gates[1]]

# router(gates, order, adj_mat, graph)