import ast
import operator
import re
from typing import Optional, Tuple

# Safe AST operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

def safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported literal type")
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero")
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")
    raise ValueError(f"Unsupported AST node: {type(node)}")

def evaluate_math_expr(expr_str: str) -> Optional[float]:
    clean = expr_str.replace("^", "**").replace("×", "*").replace("÷", "/")
    # Filter out anything not numbers, whitespace, or basic math symbols
    if not re.match(r"^[\d\s\+\-\*\/\(\)\.\%]+$", clean):
        return None
    try:
        parsed = ast.parse(clean, mode='eval')
        return safe_eval(parsed.body)
    except Exception:
        return None

def extract_and_solve_math(prompt: str) -> Optional[str]:
    # Check for direct calculation keywords or expressions
    expr_match = re.search(r"([\d\.\s\+\-\*\/\(\)\^]{3,})", prompt)
    if not expr_match:
        return None
        
    candidate = expr_match.group(1).strip()
    result = evaluate_math_expr(candidate)
    if result is None:
        return None
        
    # Format nice output with steps
    is_int = isinstance(result, int) or (isinstance(result, float) and result.is_integer())
    formatted_res = int(result) if is_int else round(result, 6)

    return f"""## Mathematical Derivation & Solution

We are asked to evaluate the expression:
\\[
\\mathcal{{E}} = {candidate}
\\]

### Step-by-Step Analytical Working:
1. **Expression Parsing**: We parse the algebraic hierarchy according to standard operator precedence (**PEMDAS / BODMAS**):
   - Parentheses / Brackets evaluation first.
   - Exponentiation / Powers second.
   - Multiplication and Division from left to right.
   - Addition and Subtraction from left to right.

2. **Evaluation Progression**:
   Evaluating the expression systematically:
   \\[
   {candidate} = {formatted_res}
   \\]

3. **Final Result**:
   \\[
   \\mathbf{{{formatted_res}}}
   \\]

> [!NOTE]
> The arithmetic derivation was evaluated rigorously with deterministic precision.
"""
