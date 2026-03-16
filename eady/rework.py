import numpy as np
import scipy.io
import sys

def generate_affine_chc(mat_file, output_file, reduced_dim=10, dt=0.01):
    print(f"Loading {mat_file}...")
    try:
        mat_data = scipy.io.loadmat(mat_file)
    except FileNotFoundError:
        print(f"Error: Could not find {mat_file}. Please ensure it is in the same directory.")
        return

    # Extract standard State-Space matrices (fallback to defaults if not found)
    # The Eady model often stores A, B, C, and E matrices.
    A_full = mat_data.get('A', None)
    B_full = mat_data.get('B', None)
    
    if A_full is None or B_full is None:
        print("Error: The .mat file does not contain standard 'A' and 'B' matrices.")
        return
        
    # Convert from sparse matrices to dense numpy arrays if necessary
    if scipy.sparse.issparse(A_full):
        A_full = A_full.toarray()
    if scipy.sparse.issparse(B_full):
        B_full = B_full.toarray()

    print(f"Original System Dimension: {A_full.shape[0]}")

    # --- 1. MODEL ORDER REDUCTION (Naive Truncation) ---
    # For a real engineering pipeline, replace this with PyMOR or control.balred
    print(f"Reducing system to {reduced_dim} dimensions...")
    A_red = A_full[:reduced_dim, :reduced_dim]
    B_red = B_full[:reduced_dim, :]

    # --- 2. DISCRETIZATION (Forward Euler) ---
    # x_{k+1} = x_k + dt * (A * x_k + B * u_k)
    # x_{k+1} = (I + dt * A) * x_k + (dt * B) * u_k
    print(f"Discretizing with Forward Euler (dt = {dt})...")
    I = np.eye(reduced_dim)
    Ad = I + dt * A_red
    Bd = dt * B_red

    # --- 3. SMT-LIB2 GENERATION ---
    print(f"Generating CHC SMT-LIB2 file: {output_file}...")
    
    # Variable names
    states = [f"x{i}" for i in range(reduced_dim)]
    next_states = [f"x{i}_next" for i in range(reduced_dim)]
    inputs = [f"u{i}" for i in range(B_red.shape[1])]
    all_vars = states + inputs

    with open(output_file, 'w') as f:
        f.write(";; Automatically generated affine loop from .mat file\n")
        f.write("(set-logic HORN)\n\n")

        # Declare the Invariant Predicate
        var_types = " ".join(["Real" for _ in all_vars])
        f.write(f"(declare-fun Inv ({var_types}) Bool)\n\n")

        # INIT RULE: All states start at 0
        f.write(";; 1. Initialization\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in all_vars]))
        f.write(")\n    (=>\n      (and\n")
        for s in states:
            f.write(f"        (= {s} 0.0)\n")
        f.write("      )\n")
        f.write(f"      (Inv {' '.join(all_vars)})\n    )\n  )\n)\n\n")

        # TRANSITION RULE: x_next = Ad * x + Bd * u
        f.write(";; 2. Transition (Affine Step)\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in all_vars]))
        f.write("\n           ")
        f.write(" ".join([f"({nv} Real)" for nv in next_states]))
        f.write(")\n    (=>\n      (and\n")
        f.write(f"        (Inv {' '.join(all_vars)})\n\n")
        
        # Write the matrix multiplication explicitly for the SMT solver
        for i in range(reduced_dim):
            # Sum up (Ad_ij * x_j)
            row_terms = []
            for j in range(reduced_dim):
                val = Ad[i, j]
                if val != 0:
                    row_terms.append(f"(* {val:.6f} {states[j]})")
            
            # Sum up (Bd_ij * u_j)
            for j in range(Bd.shape[1]):
                val = Bd[i, j]
                if val != 0:
                    row_terms.append(f"(* {val:.6f} {inputs[j]})")
                    
            # Combine terms into an addition tree
            if len(row_terms) == 0:
                f.write(f"        (= {next_states[i]} 0.0)\n")
            elif len(row_terms) == 1:
                f.write(f"        (= {next_states[i]} {row_terms[0]})\n")
            else:
                # Create nested additions for Lisp syntax: (+ a (+ b c))
                expr = row_terms[-1]
                for term in reversed(row_terms[:-1]):
                    expr = f"(+ {term} {expr})"
                f.write(f"        (= {next_states[i]} {expr})\n")

        f.write("      )\n")
        f.write(f"      (Inv {' '.join(next_states)} {' '.join(inputs)})\n    )\n  )\n)\n\n")

        # QUERY RULE: Artificial Safety Bound (e.g., x0 cannot exceed 100)
        f.write(";; 3. Safety Query\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in all_vars]))
        f.write(")\n    (=>\n      (and\n")
        f.write(f"        (Inv {' '.join(all_vars)})\n")
        f.write(f"        (> x0 100.0) ;; Adjust this to your required property\n")
        f.write("      )\n      false\n    )\n  )\n)\n\n")

        f.write("(check-sat)\n(get-model)\n")

    print(f"Success! Reduced {reduced_dim}-dimensional CHC saved to {output_file}")
    # --- 4. LQR CONTROL DESIGN ---
    print("Designing LQR Controller...")

# Define the Q matrix (Penalize state deviations)
# np.eye(reduced_dim) creates a diagonal matrix of 1s.
# Multiplying by 10.0 tells the solver that state errors are relatively expensive.
    Q = np.eye(reduced_dim) * 10.0

# Define the R matrix (Penalize actuator effort)
# Since we only have 1 input, this is a 1x1 matrix.
# Keeping it at 1.0 means we are less worried about actuator effort than state error.
    R = np.eye(Bd.shape[1]) * 1.0

# Solve the Discrete Algebraic Riccati Equation (DARE) to find matrix P
    P = scipy.linalg.solve_discrete_are(Ad, Bd, Q, R)

# Calculate the optimal feedback gain matrix K
# Formula: K = (R + B^T P B)^-1 * (B^T P A)
    R_plus_BTPB = R + Bd.T @ P @ Bd
    K = np.linalg.inv(R_plus_BTPB) @ (Bd.T @ P @ Ad)

    print("Optimal LQR Gain Vector (K):")
    print(K)

import scipy.linalg

if __name__ == "__main__":
    # You can change the target dimension here
    generate_affine_chc("eady.mat", "eady_reduced.smt2", reduced_dim=15, dt=0.01)
