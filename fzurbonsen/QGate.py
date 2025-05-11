
class QGate:
    def __init__(self, id, type, qubit1, qubit2=-1, theta=0):
        self.id = id
        self.type = type
        self.ms_id = -1
        self.theta = theta
        self.done = 0
        self.next = []
        self.prev = []
        self.time_index = 0

        if type == "RX" or type == "RY":
            self.qubit1 = qubit1
            self.qubit2 = -1
            if qubit2 != -1:
                raise AssertionError(f"Too many qubits for the gate type {self.type}!")
        elif type == "MS":
            self.qubit1 = qubit1
            self.qubit2 = qubit2
            if qubit2 == -1:
                raise AssertionError(f"Too few qubits for the gate type {self.type}!")
        else:
            raise AssertionError(f"Unknown gate type {self.type}!")

    def __str__(self):
        if self.qubit2 != -1:
            return f"id: {self.id}, type: {self.type}, qubit1: {self.qubit1}, qubit2: {self.qubit2}"
        else:
            return f"id: {self.id}, type: {self.type}, qubit1: {self.qubit1}"
