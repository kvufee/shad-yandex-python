import sys
import math
from typing import Any

PROMPT = '>>> '


def run_calc(context: dict[str, Any] | None = None) -> None:
    """Run interactive calculator session in specified namespace"""
    if context is None:
        context = {}

    builtins = {name: None for name in dir(__builtins__) if name not in ['print', 'input', 'exec', 'eval']}

    while True:
        sys.stdout.write(PROMPT)
        sys.stdout.flush()
        try:
            expression = sys.stdin.readline()
            if expression == '':
                break

            expression = expression.strip()
            result = eval(expression, {'__builtins__': builtins}, context)

            sys.stdout.write(f"{result}\n")

        except NameError as e:
            raise e

    sys.stdout.write('\n')


if __name__ == '__main__':
    context = {'math': math}
    run_calc(context)
