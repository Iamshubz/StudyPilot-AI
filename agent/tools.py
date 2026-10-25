"""agent/tools.py - Safe Arithmetic Calculator Tool for StudyPilot AI.

This module implements a strictly safe arithmetic evaluation engine using
Python's Abstract Syntax Tree (AST). It guarantees:
1. Complete isolation from eval() and exec().
2. Whitelisting of only basic arithmetic operators (+, -, *, /, //, %, **).
3. Hard limits on exponentiation to prevent CPU Denial of Service.
4. Protection against DivisionByZero and malformed syntax.
5. Deterministic, verifiable tool execution distinct from LLM text generation.
"""

import ast
import math
import operator
import re
from typing import Any, Dict, Optional, Tuple, Union

# Whitelisted operators mapped to python operator functions
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Maximum allowed base and exponent for safety
MAX_EXPONENT = 1000
MAX_BASE = 1000000
MAX_RESULT_DIGITS = 100


class SafeArithmeticEvaluator:
    """Evaluates mathematical expressions strictly using AST parsing."""

    def __init__(self, max_power: int = MAX_EXPONENT, max_base: int = MAX_BASE):
        self.max_power = max_power
        self.max_base = max_base

    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """Recursively evaluate an AST node against safe whitelisted nodes."""
        # Handle numeric constants (Python 3.8+ ast.Constant, backwards compatible)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                if isinstance(node.value, float) and not math.isfinite(node.value):
                    raise ValueError("Non-finite numbers are not supported.")
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        # Handle binary operations: a + b, a * b, etc.
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")

            left_val = self._eval_node(node.left)
            right_val = self._eval_node(node.right)

            # Division by zero check
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right_val == 0:
                raise ZeroDivisionError("Division or modulo by zero is undefined.")

            # Safety check for exponentiation to avoid CPU hang
            if op_type is ast.Pow:
                if abs(left_val) > self.max_base or abs(right_val) > self.max_power:
                    raise ValueError(
                        f"Exponentiation too large: base must be <= {self.max_base} "
                        f"and power must be <= {self.max_power}."
                    )

            try:
                result = SAFE_OPERATORS[op_type](left_val, right_val)
                if isinstance(result, float) and not math.isfinite(result):
                    raise ValueError("Calculation result is not finite.")
                # Avoid astronomical result sizes
                if isinstance(result, int) and len(str(abs(result))) > MAX_RESULT_DIGITS:
                    raise ValueError("Calculation result exceeds maximum safe representation.")
                return result
            except OverflowError:
                raise OverflowError("Arithmetic overflow: result is too large to represent.")

        # Handle unary operations: -x, +x
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            operand_val = self._eval_node(node.operand)
            return SAFE_OPERATORS[op_type](operand_val)

        else:
            raise ValueError(f"Disallowed expression element: {type(node).__name__}")

    def evaluate(self, expression: str) -> Dict[str, Any]:
        """Safely evaluates an arithmetic expression string.

        Returns a dictionary with status, result, expression, and any error message.
        """
        if not expression or not expression.strip():
            return {
                "success": False,
                "result": None,
                "expression": expression,
                "error": "Empty arithmetic expression.",
                "tool_name": "SafeArithmeticCalculator",
            }

        cleaned_expr = expression.strip()

        # Reject expressions containing dangerous characters or keywords
        if any(kw in cleaned_expr for kw in ("import", "exec", "eval", "__", "lambda", ";", ":")):
            return {
                "success": False,
                "result": None,
                "expression": cleaned_expr,
                "error": "Expression rejected: Contains prohibited keywords or syntax.",
                "tool_name": "SafeArithmeticCalculator",
            }

        try:
            parsed = ast.parse(cleaned_expr, mode="eval")
            result = self._eval_node(parsed.body)
            # Format nicely: convert float like 4.0 to int 4 if integer
            if isinstance(result, float) and result.is_integer():
                formatted_result = int(result)
            elif isinstance(result, float):
                formatted_result = round(result, 6)
            else:
                formatted_result = result

            return {
                "success": True,
                "result": formatted_result,
                "expression": cleaned_expr,
                "error": None,
                "tool_name": "SafeArithmeticCalculator",
            }
        except ZeroDivisionError as zde:
            return {
                "success": False,
                "result": None,
                "expression": cleaned_expr,
                "error": str(zde),
                "tool_name": "SafeArithmeticCalculator",
            }
        except OverflowError as oe:
            return {
                "success": False,
                "result": None,
                "expression": cleaned_expr,
                "error": str(oe),
                "tool_name": "SafeArithmeticCalculator",
            }
        except (SyntaxError, ValueError) as e:
            return {
                "success": False,
                "result": None,
                "expression": cleaned_expr,
                "error": f"Invalid expression: {str(e)}",
                "tool_name": "SafeArithmeticCalculator",
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "expression": cleaned_expr,
                "error": f"Calculation error: {str(e)}",
                "tool_name": "SafeArithmeticCalculator",
            }


# Singleton instance
calculator = SafeArithmeticEvaluator()


def calculate(expression: str) -> Dict[str, Any]:
    """Public functional interface for tool invocation."""
    return calculator.evaluate(expression)


# Regex patterns to detect arithmetic questions in chat
ARITHMETIC_PATTERNS = [
    r"^\s*(?:calculate|compute|solve|what\s+is|evaluate)?\s*([0-9\.\s\+\-\*\/\(\)\%\^]+)\s*[\?\.]?\s*$",
    r"calculate\s+([0-9\.\s\+\-\*\/\(\)\%\^]+)",
    r"compute\s+([0-9\.\s\+\-\*\/\(\)\%\^]+)",
    r"solve\s+([0-9\.\s\+\-\*\/\(\)\%\^]+)",
    r"what\s+is\s+([0-9\.\s\+\-\*\/\(\)\%\^]+)\s*\?",
]


def detect_and_execute_arithmetic(text: str) -> Optional[Dict[str, Any]]:
    """Detects if user message is asking for a pure arithmetic calculation.

    If so, executes the safe calculator tool and returns structured tool output.
    Returns None if the message is general conversational text.
    """
    text_clean = text.strip()

    # Avoid false positives on general English questions
    if len(text_clean) > 80:
        return None

    for pattern in ARITHMETIC_PATTERNS:
        match = re.search(pattern, text_clean, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            # Replace ^ with ** for power
            candidate_norm = candidate.replace("^", "**")
            # Ensure it contains at least one digit and one arithmetic operator
            has_digit = any(c.isdigit() for c in candidate_norm)
            has_op = any(op in candidate_norm for op in ("+", "-", "*", "/", "%"))

            if has_digit and has_op:
                res = calculate(candidate_norm)
                if res["success"]:
                    return res
                # If it had division by zero or clear syntax error in math, return error response
                if res.get("error") and "zero" in res["error"].lower():
                    return res

    return None
