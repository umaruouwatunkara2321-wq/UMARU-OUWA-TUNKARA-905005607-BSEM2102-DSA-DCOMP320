"""
main.py
-------
DCOMP320 - Data Structures and Algorithm
Assignment: Stacks Implementation

Student : Umaru Ouwa Tunkara
Student ID: 905005607
Programme : BSEM2102
Semester  : 03&05  (September 2026 – February 2027)
Examiner  : Amandus Benjamin Coker

Overview:
    Reads mathematical expressions from input.txt, evaluates each one using a
    custom stack-based algorithm (two-stack / operator-precedence method), and
    writes the results to output.txt.  Separator lines (-----) present in the
    input are preserved in the output.

Usage:
    python main.py
"""

import os
import re

# ---------------------------------------------------------------------------
# 1.  STACK CLASS
# ---------------------------------------------------------------------------

class Stack:
    """
    A generic stack data structure implemented using a Python list.

    Supports the fundamental LIFO (Last-In, First-Out) operations:
        push   – add an item to the top
        pop    – remove and return the item at the top
        peek   – inspect the top item without removing it
        is_empty – check whether the stack has no items
        size   – return the number of items currently on the stack
    """

    def __init__(self):
        """Initialise an empty stack."""
        self._items = []

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def push(self, item):
        """
        Push *item* onto the top of the stack.

        Parameters
        ----------
        item : any
            The value to be stored.
        """
        self._items.append(item)

    def pop(self):
        """
        Remove and return the item at the top of the stack.

        Returns
        -------
        any
            The item that was on top.

        Raises
        ------
        IndexError
            If the stack is empty.
        """
        if self.is_empty():
            raise IndexError("pop() called on an empty stack.")
        return self._items.pop()

    def peek(self):
        """
        Return the item at the top of the stack without removing it.

        Returns
        -------
        any
            The item currently on top.

        Raises
        ------
        IndexError
            If the stack is empty.
        """
        if self.is_empty():
            raise IndexError("peek() called on an empty stack.")
        return self._items[-1]

    def is_empty(self):
        """Return True if the stack contains no items, False otherwise."""
        return len(self._items) == 0

    def size(self):
        """Return the number of items currently on the stack."""
        return len(self._items)

    # ------------------------------------------------------------------
    # Helper / dunder
    # ------------------------------------------------------------------

    def __repr__(self):
        return f"Stack({self._items!r})"


# ---------------------------------------------------------------------------
# 2.  TOKENISER
# ---------------------------------------------------------------------------

def tokenise(expression):
    """
    Split a mathematical expression string into a list of typed tokens.

    Each token is a tuple (type, value) where *type* is one of:
        'NUMBER'    – a numeric literal (int or float)
        'OP'        – an operator character: +  -  *  /
        'LPAREN'    – opening parenthesis '('
        'RPAREN'    – closing parenthesis ')'

    Parameters
    ----------
    expression : str
        The raw expression string, e.g. '3 + 5 * 2'.

    Returns
    -------
    list of tuple
        Ordered sequence of (type, value) tokens.

    Raises
    ------
    ValueError
        If the expression contains an unrecognised character.
    """
    tokens = []
    # Regex pattern: floats/ints, operators, parentheses, or any other char
    token_pattern = re.compile(
        r'\d+\.?\d*'          # integer or decimal number
        r'|[+\-*/]'           # operators
        r'|[()]'              # parentheses
        r'|[^\s]'             # any other non-whitespace → will trigger an error
    )

    for match in token_pattern.finditer(expression):
        raw = match.group()
        if re.fullmatch(r'\d+\.?\d*', raw):
            # Convert to int if possible, otherwise float
            value = float(raw) if '.' in raw else int(raw)
            tokens.append(('NUMBER', value))
        elif raw in '+-*/':
            tokens.append(('OP', raw))
        elif raw == '(':
            tokens.append(('LPAREN', raw))
        elif raw == ')':
            tokens.append(('RPAREN', raw))
        else:
            raise ValueError(
                f"Invalid character '{raw}' found in expression: '{expression}'"
            )

    return tokens


# ---------------------------------------------------------------------------
# 3.  EXPRESSION EVALUATOR  (two-stack algorithm)
# ---------------------------------------------------------------------------

# Operator precedence table
_PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2}


def _apply_operator(operand_stack, operator_stack):
    """
    Pop one operator and two operands from the respective stacks, apply the
    operation, and push the result back onto the operand stack.

    Parameters
    ----------
    operand_stack  : Stack
    operator_stack : Stack

    Raises
    ------
    ZeroDivisionError
        If division by zero is attempted.
    ValueError
        If there are insufficient operands available.
    """
    if operand_stack.size() < 2:
        raise ValueError("Insufficient operands for the operator.")

    right  = operand_stack.pop()
    left   = operand_stack.pop()
    op     = operator_stack.pop()

    if op == '+':
        result = left + right
    elif op == '-':
        result = left - right
    elif op == '*':
        result = left * right
    elif op == '/':
        if right == 0:
            raise ZeroDivisionError(
                f"Division by zero: {left} / {right}"
            )
        result = left / right
    else:
        raise ValueError(f"Unknown operator: '{op}'")

    operand_stack.push(result)


def evaluate_expression(expression):
    """
    Evaluate a single infix mathematical expression using two stacks.

    Algorithm (two-stack / operator-precedence):
        1. Tokenise the expression.
        2. For each token:
           - NUMBER  → push onto the operand stack.
           - LPAREN  → push onto the operator stack.
           - RPAREN  → apply operators until a matching LPAREN is found.
           - OP      → apply operators with higher-or-equal precedence first,
                       then push the current operator.
        3. After all tokens are processed, apply any remaining operators.
        4. The single remaining item on the operand stack is the result.

    Parameters
    ----------
    expression : str
        A well-formed (or ill-formed – errors are reported) infix expression.

    Returns
    -------
    int or float
        The numerical result of evaluating the expression.

    Raises
    ------
    ValueError
        For invalid expressions (bad characters, mismatched parentheses, etc.)
    ZeroDivisionError
        When the expression attempts to divide by zero.
    """
    expression = expression.strip()
    if not expression:
        raise ValueError("Expression is empty.")

    tokens = tokenise(expression)   # may raise ValueError for invalid chars

    if not tokens:
        raise ValueError("Expression contains no valid tokens.")

    operand_stack  = Stack()
    operator_stack = Stack()

    prev_type = None   # used to detect consecutive operators / missing operands

    for token_type, token_value in tokens:

        if token_type == 'NUMBER':
            operand_stack.push(token_value)

        elif token_type == 'LPAREN':
            operator_stack.push(token_value)

        elif token_type == 'RPAREN':
            # Apply operators until the matching '(' is found
            matched = False
            while not operator_stack.is_empty():
                if operator_stack.peek() == '(':
                    operator_stack.pop()   # discard the '('
                    matched = True
                    break
                _apply_operator(operand_stack, operator_stack)
            if not matched:
                raise ValueError(
                    f"Unmatched closing parenthesis ')' in expression: '{expression}'"
                )

        elif token_type == 'OP':
            # Guard: two operators in a row (e.g. '5 + *') is invalid
            # Exception: unary minus at the start or after '(' is NOT supported
            # by this implementation; report it clearly.
            if prev_type == 'OP':
                raise ValueError(
                    f"Consecutive operators found in expression: '{expression}'"
                )
            if prev_type is None and token_value in ('+', '-', '*', '/'):
                raise ValueError(
                    f"Expression starts with an operator: '{expression}'"
                )

            # Apply any operators on the stack with higher or equal precedence
            while (
                not operator_stack.is_empty()
                and operator_stack.peek() in _PRECEDENCE
                and _PRECEDENCE[operator_stack.peek()] >= _PRECEDENCE[token_value]
            ):
                _apply_operator(operand_stack, operator_stack)

            operator_stack.push(token_value)

        prev_type = token_type

    # Guard: expression ending with an operator
    if prev_type == 'OP':
        raise ValueError(
            f"Expression ends with an operator: '{expression}'"
        )

    # Apply all remaining operators
    while not operator_stack.is_empty():
        if operator_stack.peek() == '(':
            raise ValueError(
                f"Unmatched opening parenthesis '(' in expression: '{expression}'"
            )
        _apply_operator(operand_stack, operator_stack)

    # The operand stack should now hold exactly one value
    if operand_stack.size() != 1:
        raise ValueError(
            f"Could not reduce expression to a single result: '{expression}'"
        )

    result = operand_stack.pop()

    # Return an int when the result is a whole number (e.g. 13.0 → 13)
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


# ---------------------------------------------------------------------------
# 4.  INPUT FILE READER
# ---------------------------------------------------------------------------

SEPARATOR_PATTERN = re.compile(r'^-{3,}\s*$')   # three or more hyphens


def is_separator(line):
    """Return True if *line* is a separator line (e.g. '-----')."""
    return bool(SEPARATOR_PATTERN.match(line.strip()))


def read_input_file(filepath):
    """
    Read the input file and return a list of line descriptors.

    Each element is a dict with keys:
        'type'  : 'expression' | 'separator' | 'blank'
        'raw'   : the original line text (without newline)

    Parameters
    ----------
    filepath : str
        Path to input.txt.

    Returns
    -------
    list of dict

    Raises
    ------
    FileNotFoundError
        If *filepath* does not exist.
    IOError
        On other file-read failures.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Input file not found: '{filepath}'\n"
            "Please create input.txt in the project directory."
        )

    lines = []
    with open(filepath, 'r', encoding='utf-8') as fh:
        for raw_line in fh:
            line = raw_line.rstrip('\n').rstrip('\r')
            if is_separator(line):
                lines.append({'type': 'separator', 'raw': line})
            elif line.strip() == '':
                lines.append({'type': 'blank', 'raw': line})
            else:
                lines.append({'type': 'expression', 'raw': line})

    return lines


# ---------------------------------------------------------------------------
# 5.  OUTPUT FILE WRITER
# ---------------------------------------------------------------------------

def write_output_file(filepath, results):
    """
    Write evaluated results (and preserved separators/blanks) to *filepath*.

    Parameters
    ----------
    filepath : str
        Path to output.txt.
    results  : list of dict
        Each element has keys:
            'type'   : 'result' | 'separator' | 'blank' | 'error'
            'value'  : the string to write for this line
    """
    with open(filepath, 'w', encoding='utf-8') as fh:
        for item in results:
            fh.write(str(item['value']) + '\n')


# ---------------------------------------------------------------------------
# 6.  MAIN PROCESSING PIPELINE
# ---------------------------------------------------------------------------

def process_file(input_path, output_path):
    """
    Orchestrate the complete input → evaluate → output pipeline.

    Parameters
    ----------
    input_path  : str
        Path to input.txt.
    output_path : str
        Path to output.txt.

    Returns
    -------
    tuple(int, int)
        (expressions_processed, error_count)
    """
    lines = read_input_file(input_path)   # may raise FileNotFoundError / IOError

    expression_count = 0
    error_count      = 0
    output_items     = []

    for line_info in lines:
        if line_info['type'] == 'separator':
            output_items.append({'type': 'separator', 'value': line_info['raw']})

        elif line_info['type'] == 'blank':
            output_items.append({'type': 'blank', 'value': ''})

        elif line_info['type'] == 'expression':
            expression_count += 1
            expr = line_info['raw']
            try:
                result = evaluate_expression(expr)
                output_items.append({'type': 'result', 'value': result})
                print(f"  OK  | '{expr}' = {result}")
            except ZeroDivisionError as exc:
                error_count += 1
                msg = f"ERROR: {exc}"
                output_items.append({'type': 'error', 'value': msg})
                print(f"  ERR | '{expr}' -> {msg}")
            except ValueError as exc:
                error_count += 1
                msg = f"ERROR: {exc}"
                output_items.append({'type': 'error', 'value': msg})
                print(f"  ERR | '{expr}' -> {msg}")

    write_output_file(output_path, output_items)
    return expression_count, error_count


# ---------------------------------------------------------------------------
# 7.  ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    """
    Entry point for the stack-based expression evaluator.

    Resolves paths relative to this script's own directory so the program
    works correctly regardless of the terminal's current working directory.
    """
    base_dir    = os.path.dirname(os.path.abspath(__file__))
    input_path  = os.path.join(base_dir, 'input.txt')
    output_path = os.path.join(base_dir, 'output.txt')

    print("=" * 60)
    print("  DCOMP320 — Stack-Based Expression Evaluator")
    print("  Student : Umaru Ouwa Tunkara  |  ID: 905005607")
    print("=" * 60)
    print(f"  Input  : {input_path}")
    print(f"  Output : {output_path}")
    print("-" * 60)

    try:
        expr_count, err_count = process_file(input_path, output_path)
    except FileNotFoundError as exc:
        print(f"\n[ERROR] {exc}")
        return
    except IOError as exc:
        print(f"\n[ERROR] File I/O failure: {exc}")
        return

    print("-" * 60)
    print(f"  Expressions processed : {expr_count}")
    print(f"  Errors encountered    : {err_count}")
    print("-" * 60)

    if err_count == 0:
        print("  Processing completed successfully.")
    else:
        print(f"  Processing completed with {err_count} error(s).")
        print("  Check output.txt for details on failed expressions.")

    print(f"  Results written to output.txt")
    print("=" * 60)


if __name__ == "__main__":
    main()
