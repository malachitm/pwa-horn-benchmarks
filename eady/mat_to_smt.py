import os
import argparse
import numpy as np
import scipy.io
import scipy.linalg
import sys

def generate_lqr_chc(mat_file, reduced_dim, dt=0.01, v_max=12.0, singleton_init=False):
    print(f"Loading {mat_file}...")
    try:
        mat_data = scipy.io.loadmat(mat_file)
    except FileNotFoundError:
        print(f"Error: Could not find {mat_file}.")
        return

    A_full = mat_data.get('A')
    B_full = mat_data.get('B')
    
    if A_full is None or B_full is None:
        print("Error: The .mat file does not contain 'A' and 'B' matrices.")
        return
        
    if scipy.sparse.issparse(A_full): A_full = A_full.toarray()
    if scipy.sparse.issparse(B_full): B_full = B_full.toarray()

    # Safety check for dimensions
    max_dim = A_full.shape[0]
    if reduced_dim > max_dim:
        print(f"Warning: Requested {reduced_dim} dimensions, but system only has {max_dim}. Using {max_dim}.")
        reduced_dim = max_dim

    # --- 1. DYNAMIC FILENAME GENERATION ---
    base_name = os.path.splitext(os.path.basename(mat_file))[0]
    output_file = f"{base_name}_lqr_closed_loop_{reduced_dim}.smt2"

    # --- 2. MODEL ORDER REDUCTION ---
    print(f"Reducing system to {reduced_dim} dimensions...")
    A_red = A_full[:reduced_dim, :reduced_dim]
    B_red = B_full[:reduced_dim, :]

    # --- 3. DISCRETIZATION (Forward Euler) ---
    print(f"Discretizing (dt = {dt})...")
    I = np.eye(reduced_dim)
    Ad = I + dt * A_red
    Bd = dt * B_red

    # --- 4. LQR CONTROL DESIGN ---
    print("Designing Optimal LQR Controller...")
    Q = np.eye(reduced_dim) * 10.0  
    R = np.eye(Bd.shape[1]) * 1.0   
    
    P = scipy.linalg.solve_discrete_are(Ad, Bd, Q, R)
    R_plus_BTPB = R + Bd.T @ P @ Bd
    K = np.linalg.inv(R_plus_BTPB) @ (Bd.T @ P @ Ad)
    
    A_closed = Ad - Bd @ K

    # --- 5. SMT-LIB2 GENERATION ---
    print(f"Generating CHC SMT-LIB2 file: {output_file}...")
    states = [f"x{i}" for i in range(reduced_dim)]
    next_states = [f"x{i}_next" for i in range(reduced_dim)]
    
    with open(output_file, 'w') as f:
        f.write(f";; Automatically generated {reduced_dim}D closed-loop LQR CHC for {base_name}\n")
        if singleton_init:
            f.write(";; Note: Singleton initialization applied (all states start exactly at 0.0)\n")
        f.write("(set-logic HORN)\n\n")

        var_types = " ".join(["Real" for _ in states])
        f.write(f"(declare-fun Inv ({var_types}) Bool)\n\n")

        # INIT RULE
        f.write(";; 1. Initialization\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in states]))
        f.write(")\n    (=>\n      (and\n")
        
        # Apply singleton logic if the flag was used
        if singleton_init:
            for s in states:
                f.write(f"        (= {s} 0.0)\n")
        else:
            for s in states:
                f.write(f"        (<= {s} 0.1)\n")
                f.write(f"        (>= {s} -0.1)\n")
                
        f.write("      )\n")
        f.write(f"      (Inv {' '.join(states)})\n    )\n  )\n)\n\n")

        # TRANSITION RULE
        f.write(";; 2. Transition (Closed-Loop Affine Step)\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in states]))
        f.write("\n           ")
        f.write(" ".join([f"({nv} Real)" for nv in next_states]))
        f.write(")\n    (=>\n      (and\n")
        f.write(f"        (Inv {' '.join(states)})\n\n")
        
        for i in range(reduced_dim):
            row_terms = []
            for j in range(reduced_dim):
                val = A_closed[i, j]
                if abs(val) > 1e-8:
                    row_terms.append(f"(* {val:.6f} {states[j]})")
            
            if not row_terms:
                f.write(f"        (= {next_states[i]} 0.0)\n")
            elif len(row_terms) == 1:
                f.write(f"        (= {next_states[i]} {row_terms[0]})\n")
            else:
                expr = row_terms[-1]
                for term in reversed(row_terms[:-1]):
                    expr = f"(+ {term} {expr})"
                f.write(f"        (= {next_states[i]} {expr})\n")

        f.write("      )\n")
        f.write(f"      (Inv {' '.join(next_states)})\n    )\n  )\n)\n\n")

        # QUERY RULE
        f.write(f";; 3. Safety Query (Actuator Saturation > {v_max}V or < -{v_max}V)\n")
        f.write("(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in states]))
        f.write(")\n    (=>\n      (and\n")
        f.write(f"        (Inv {' '.join(states)})\n")
        
        u_terms = []
        for j in range(reduced_dim):
            val = -K[0, j]
            if abs(val) > 1e-8:
                u_terms.append(f"(* {val:.6f} {states[j]})")
                
        if u_terms:
            if len(u_terms) == 1:
                u_expr = u_terms[0]
            else:
                u_expr = u_terms[-1]
                for term in reversed(u_terms[:-1]):
                    u_expr = f"(+ {term} {u_expr})"
                    
            f.write("        (or\n")
            f.write(f"          (> {u_expr} {v_max:.1f})\n")
            f.write(f"          (< {u_expr} -{v_max:.1f})\n")
            f.write("        )\n")
        
        f.write("      )\n      false\n    )\n  )\n)\n\n")

        f.write("(check-sat)\n(get-model)\n")

    print(f"Success! Saved to {output_file}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate optimal LQR closed-loop CHC from a .mat file.")
    parser.add_argument("mat_file", type=str, help="Path to the input .mat file (e.g., eady.mat)")
    parser.add_argument("dimensions", type=int, help="Target number of dimensions for the reduced system")
    parser.add_argument("--singleton", action="store_true", help="Initialize all states to exactly 0.0 instead of a bounding box")
    
    args = parser.parse_args()
    
    if args.dimensions <= 0:
        print("Error: Dimensions must be a positive integer.")
        sys.exit(1)
        
    generate_lqr_chc(args.mat_file, args.dimensions, singleton_init=args.singleton)