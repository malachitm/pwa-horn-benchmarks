import xml.etree.ElementTree as ET
import ast
import re
import sys

# --- Helper Functions for Math Parsing ---

def ast_to_smtlib(node):
    """Recursively converts a Python AST math expression to SMT-LIB2 prefix notation."""
    if isinstance(node, ast.BinOp):
        op_map = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}
        op = op_map[type(node.op)]
        left = ast_to_smtlib(node.left)
        right = ast_to_smtlib(node.right)
        return f"({op} {left} {right})"
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        # Handle negative numbers/variables like -606.16*x1
        return f"(- {ast_to_smtlib(node.operand)})"
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):  # Python 3.8+
        return str(node.value)
    else:
        raise ValueError(f"Unsupported AST node: {type(node)}")
    
def sanitize_spaceex_xml(xml_file):
    """
    SpaceEx files contain unescaped '&' and '<' characters in 
    math blocks, which breaks standard XML parsers. This escapes them.
    """
    with open(xml_file, 'r') as f:
        content = f.read()

    def escape_match(match):
        tag = match.group(1)
        inner_text = match.group(2)
        # Escape & first so we don't double escape existing entities
        inner_text = inner_text.replace('&', '&amp;')
        inner_text = inner_text.replace('<', '&lt;')
        inner_text = inner_text.replace('>', '&gt;')
        return f"<{tag}>{inner_text}</{tag}>"

    # Find everything inside <invariant> and <flow> tags and escape it
    content = re.sub(r'<(invariant|flow)>(.*?)</\1>', escape_match, content, flags=re.DOTALL)
    
    # Return the parsed root directly
    return ET.fromstring(content)

def parse_equation_to_prefix(eq_string):
    """Parses a string like 'A * x + B' into SMT-LIB prefix format."""
    tree = ast.parse(eq_string.strip(), mode='eval')
    return ast_to_smtlib(tree.body)

def parse_relation_to_prefix(rel_string):
    """Handles relations like 'y1 == x25' or 't <= stoptime'."""
    # SpaceEx uses ==, <=, >=. SMT-LIB uses =, <=, >=
    match = re.split(r'(==|<=|>=|<|>)', rel_string.strip())
    if len(match) == 3:
        left, op, right = match
        op = "=" if op == "==" else op
        return f"({op} {left.strip()} {right.strip()})"
    return rel_string # Fallback

# --- Main Parser ---

def convert_spaceex_to_chc(xml_file, output_file):
    # Use our custom sanitizer to bypass the invalid XML tokens
    root = sanitize_spaceex_xml(xml_file)

    # --- 1. Robustly find the core component (Ignoring Namespaces) ---
    core_comp = None
    for elem in root.iter():
        if elem.tag.endswith('component'):
            # Prioritize 'core_component', otherwise keep the first one found
            if elem.get('id') == 'core_component':
                core_comp = elem
                break
            elif core_comp is None:
                core_comp = elem
                
    if core_comp is None:
        raise ValueError("Could not find any <component> tag in the XML file.")

    # --- 2. Extract Parameters ---
    params = []
    for elem in core_comp.iter():
        if elem.tag.endswith('param'):
            name = elem.get('name')
            if name:
                params.append(name)
    
    all_vars = params + ["dt"]

    # --- 3. Extract Invariant and Flow ---
    location = None
    for elem in core_comp.iter():
        if elem.tag.endswith('location'):
            location = elem
            break

    invariant_text = ""
    flow_text = ""
    if location is not None:
        for elem in location.iter():
            if elem.tag.endswith('invariant') and elem.text:
                invariant_text = elem.text
            elif elem.tag.endswith('flow') and elem.text:
                flow_text = elem.text

    # Parse Invariants
    invariants = [inv.strip() for inv in invariant_text.split('&') if inv.strip()]
    smt_invariants = [parse_relation_to_prefix(inv) for inv in invariants]

    # Parse Flows (Derivatives)
    flows = [f.strip() for f in flow_text.split('&') if f.strip()]
    derivatives = {}
    for flow in flows:
        if "==" in flow:
            lhs, rhs = flow.split("==")
            lhs = lhs.replace("'", "").strip() # Remove derivative tick
            rhs = rhs.strip()
            derivatives[lhs] = parse_equation_to_prefix(rhs)

    # --- 4. Generate SMT-LIB2 Output ---
    with open(output_file, 'w') as f:
        f.write("(set-logic HORN)\n\n")

        # Declare the Invariant Predicate
        var_types = " ".join(["Real" for _ in all_vars])
        f.write(f";; State Predicate\n")
        f.write(f"(declare-fun Inv ({var_types}) Bool)\n\n")

        # Initial State Rule (Assuming all 0s as placeholder)
        f.write(";; 1. Initial State\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in all_vars]))
        f.write(")\n    (=>\n      (and\n")
        for v in params:
            f.write(f"        (= {v} 0.0)\n")
        f.write(f"        (> dt 0.0)\n") # dt must be positive
        f.write("      )\n")
        f.write(f"      (Inv {' '.join(all_vars)})\n    )\n  )\n)\n\n")

        # Transition Rule (Forward Euler)
        next_vars = [f"{v}_next" for v in params]
        f.write(";; 2. Transition Rule (Forward Euler Discretization)\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in all_vars]))
        f.write("\n           ")
        f.write(" ".join([f"({nv} Real)" for nv in next_vars]))
        f.write(")\n    (=>\n      (and\n")
        f.write(f"        (Inv {' '.join(all_vars)})\n")
        
        for inv in smt_invariants:
            f.write(f"        {inv}\n")
            
        f.write("\n        ;; Dynamics\n")
        for v in params:
            if v in derivatives:
                if v == 't': # Time is a special case in Euler
                    f.write(f"        (= {v}_next (+ {v} dt))\n")
                else:
                    f.write(f"        (= {v}_next (+ {v} (* dt {derivatives[v]})))\n")
            else:
                # If a variable has no derivative (like u1 or stoptime), it stays constant
                f.write(f"        (= {v}_next {v})\n")

        f.write("      )\n")
        f.write(f"      (Inv {' '.join(next_vars)} dt)\n    )\n  )\n)\n\n")

        # Query Rule (Safety Property Placeholder)
        f.write(";; 3. Query / Safety Property (Placeholder: prove y1 never exceeds 100)\n(assert\n  (forall (")
        f.write(" ".join([f"({v} Real)" for v in all_vars]))
        f.write(")\n    (=>\n      (and\n")
        f.write(f"        (Inv {' '.join(all_vars)})\n")
        f.write(f"        (> y1 100.0) ;; Replace this with your unsafe state\n")
        f.write("      )\n      false\n    )\n  )\n)\n\n")

        f.write("(check-sat)\n(get-model)\n")

    print(f"Successfully generated {output_file}")

# To run the script:
if __name__ == "__main__":
    # Replace 'model.sspaceex' with your actual filename
    convert_spaceex_to_chc("1.xml", "model_chc.smt2")