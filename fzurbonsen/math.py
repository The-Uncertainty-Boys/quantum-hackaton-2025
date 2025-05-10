import numpy as np

# Define the gates
def ry_matrix(theta):
    """ Return the matrix for an RY rotation by angle theta """
    return np.array([[np.cos(theta/2), -np.sin(theta/2)],
                     [np.sin(theta/2), np.cos(theta/2)]])

def rx_matrix(theta):
    """ Return the matrix for an RX rotation by angle theta """
    return np.array([[np.cos(theta/2), -1j*np.sin(theta/2)],
                     [-1j*np.sin(theta/2), np.cos(theta/2)]])

def ms_matrix(theta):
    """ Return the matrix for an MS gate with angle theta for two qubits """
    I = np.eye(2)
    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)  # The XX interaction part in 4x4 space
    return np.cos(theta/2) * np.eye(4) - 1j * np.sin(theta/2) * XX

# Define the total unitary matrix
def total_unitary(angle):
    """ Return the unitary matrix for the full sequence of gates """
    # First apply RY(-pi/2) on control and target qubits
    U_ry1 = np.kron(ry_matrix(-np.pi/2), np.eye(2))  # RY on qubit 1, identity on qubit 2
    U_ry2 = np.kron(np.eye(2), ry_matrix(-np.pi/2))  # Identity on qubit 1, RY on qubit 2
    
    # Apply MS gate (Mølmer-Sørensen gate with pi/4)
    U_ms1 = ms_matrix(np.pi/4)
    
    # Apply RX(-angle/2) on the target qubit
    U_rx = np.kron(np.eye(2), rx_matrix(-angle/2))  # Identity on qubit 1, RX on qubit 2
    
    # Apply MS gate with -pi/4
    U_ms2 = ms_matrix(-np.pi/4)
    
    # Apply final RY(pi/2) on control and target qubits
    U_ry3 = np.kron(ry_matrix(np.pi/2), np.eye(2))  # RY on qubit 1, identity on qubit 2
    U_ry4 = np.kron(np.eye(2), ry_matrix(np.pi/2))  # Identity on qubit 1, RY on qubit 2
    
    # Combine all gates: We will apply each to the 2 qubits (control and target)
    # We will combine them by multiplying the matrices in sequence:
    # U = U_ry1 * U_ry2 * U_ms1 * U_rx * U_ms2 * U_ry3 * U_ry4
    
    U_total = np.dot(U_ry1, np.dot(U_ry2, np.dot(U_ms1, np.dot(U_rx, np.dot(U_ms2, np.dot(U_ry3, U_ry4))))))
    
    return U_total

# Define the angle for controlled phase shift
angle = np.pi/2

# Compute the unitary matrix for the gate sequence
U = total_unitary(angle)
np.set_printoptions(threshold=np.inf, linewidth=np.inf, precision=5, suppress=True)

# Print the resulting unitary matrix
print("Unitary matrix for the gate sequence:")
print(U)

# Optionally save to file
with open("qft_output.txt", "w") as f:
    f.write("Unitary matrix for the gate sequence:\n")
    f.write(str(U))
