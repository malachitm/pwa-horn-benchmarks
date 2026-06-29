import numpy as np
import scipy.linalg
import os

# Configuration
DIMENSIONS = [5, 10, 15, 20, 25]
LEVELS = [1, 2, 3, 4, 5]
INSTANCES_PER_COMBINATION = 5
DT = 0.05 
STEPS_FOR_SIMULATION = 100 

os.makedirs("rand_bench", exist_ok=True)

def generate_base_eigenvalues(n, level):
    eigenvalues = []
    while len(eigenvalues) < n:
        remaining = n - len(eigenvalues)
        if level == 1:
            eigenvalues.append(np.random.uniform(-5.0, -1.0))
        elif level == 2:
            if remaining >= 2:
                real_part = np.random.uniform(-0.5, -0.01)
                imag_part = np.random.uniform(1.0, 3.0)
                eigenvalues.extend([complex(real_part, imag_part), complex(real_part, -imag_part)])
            else:
                eigenvalues.append(np.random.uniform(-0.5, -0.01))
        elif level == 3:
            if remaining >= 2:
                imag_part = np.random.uniform(1.0, 5.0)
                eigenvalues.extend([complex(0, imag_part), complex(0, -imag_part)])
            else:
                eigenvalues.append(0.0)
        elif level == 4:
            eigenvalues.append(np.random.uniform(0.1, 1.0))
        elif level == 5:
            if remaining % 2 == 0:
                eigenvalues.append(np.random.uniform(-1000.0, -500.0))
            else:
                eigenvalues.append(np.random.uniform(-0.01, -0.001))
    return eigenvalues

def build_A_matrix(eigenvalues):
    n = len(eigenvalues)
    Lambda = np.zeros((n, n))
    i = 0
    while i < n:
        val = eigenvalues[i]
        if np.iscomplex(val):
            a = val.real
            b = val.imag
            Lambda[i, i] = a
            Lambda[i, i+1] = -b
            Lambda[i+1, i] = b
            Lambda[i+1, i+1] = a
            i += 2
        else:
            Lambda[i, i] = val.real
            i += 1
            
    Q = np.random.randn(n, n)
    while np.abs(np.linalg.det(Q)) < 1e-5:
        Q = np.random.randn(n, n)
        
    Q_inv = np.linalg.inv(Q)
    A = Q @ Lambda @ Q_inv
    return A

def generate_smt_chc(n, level, instance_id, base_eigs):
    eigenvalues = []
    for _ in range(n // len(base_eigs)):
        eigenvalues.extend(base_eigs)
        
    A_cont = build_A_matrix(eigenvalues)
    C = np.random.randn(1, n)
    A_disc = scipy.linalg.expm(A_cont * DT)
    
    x = np.random.uniform(-1, 1, (n, 1))
    max_output = 0
    for _ in range(STEPS_FOR_SIMULATION):
        y = C @ x
        max_output = max(max_output, abs(y[0, 0]))
        x = A_disc @ x
        
    safety_threshold = max_output * 1.2
    
    state_vars = " ".join([f"x{i}" for i in range(n)])
    state_decls = " ".join([f"(x{i} Real)" for i in range(n)])
    next_state_decls = " ".join([f"(x{i}_next Real)" for i in range(n)])
    
    lines = []
    lines.append(f";; Auto-generated {n}D LTI System")
    lines.append(f";; Complexity Level: {level} | Instance: {instance_id}")
    lines.append("(set-logic HORN)")
    lines.append("")
    
    inv_types = " ".join(["Real" for _ in range(n)])
    lines.append(f"(declare-fun Inv ({inv_types}) Bool)")
    lines.append("")
    
    lines.append(";; 1. Initialization")
    lines.append(f"(assert\n  (forall ({state_decls})\n    (=>\n      (and")
    for i in range(n):
        lines.append(f"        (<= x{i} 1.0)\n        (>= x{i} -1.0)")
    lines.append(f"      )\n      (Inv {state_vars})\n    )\n  )\n)")
    lines.append("")
    
    lines.append(";; 2. Transition")
    lines.append(f"(assert\n  (forall ({state_decls} {next_state_decls})\n    (=>\n      (and\n        (Inv {state_vars})")
    for i in range(n):
        # FIX: Build list of clean expressions directly
        equation_terms = [f"(* {A_disc[i, j]:.6f} x{j})" for j in range(n)]
        while len(equation_terms) > 1:
            term1 = equation_terms.pop(0)
            term2 = equation_terms.pop(0)
            equation_terms.insert(0, f"(+ {term1} {term2})")
            
        lines.append(f"        (= x{i}_next {equation_terms[0]})")
    lines.append(f"      )\n      (Inv {" ".join([f"x{i}_next" for i in range(n)])})\n    )\n  )\n)")
    lines.append("")
    
    lines.append(";; 3. Safety Query")
    lines.append(f"(assert\n  (forall ({state_decls})\n    (=>\n      (and\n        (Inv {state_vars})")
    
    # FIX: Clean linear combination scaling for output
    c_terms = [f"(* {C[0, j]:.6f} x{j})" for j in range(n)]
    while len(c_terms) > 1:
        term1 = c_terms.pop(0)
        term2 = c_terms.pop(0)
        c_terms.insert(0, f"(+ {term1} {term2})")
        
    lines.append(f"        (or\n          (> {c_terms[0]} {safety_threshold:.6f})\n          (< {c_terms[0]} -{safety_threshold:.6f})\n        )")
    lines.append(f"      )\n      false\n    )\n  )\n)")
    lines.append("")
    lines.append("(check-sat)")
    lines.append("(get-model)")
    
    filename = f"rand_bench/benchmark_n{n}_lvl{level}_inst{instance_id}.smt2"
    with open(filename, "w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    base_eigenvalue_pool = {}
    for lvl in LEVELS:
        base_eigenvalue_pool[lvl] = {}
        for inst in range(INSTANCES_PER_COMBINATION):
            base_eigenvalue_pool[lvl][inst] = generate_base_eigenvalues(5, lvl)
            
    count = 0
    print("Generating 125 LTI benchmarks...")
    for n in DIMENSIONS:
        for lvl in LEVELS:
            for inst in range(INSTANCES_PER_COMBINATION):
                base_eigs = base_eigenvalue_pool[lvl][inst]
                generate_smt_chc(n, lvl, inst, base_eigs)
                count += 1
    
    print(f"Successfully generated {count} benchmarks in the 'rand_bench' folder.")