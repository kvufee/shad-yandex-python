import dis
import types

from collections import defaultdict
from typing import Dict


def count_operations(source_code: types.CodeType) -> dict[str, int]:
    """Count byte code operations in given source code.

    :param source_code: the bytecode operation names to be extracted from
    :return: operation counts
    """
    counts: Dict[str, int] = defaultdict(int)

    def traverse_code(co: types.CodeType) -> None:
        for instruction in dis.get_instructions(co):
            counts[instruction.opname] += 1
            if instruction.argval and isinstance(instruction.argval, types.CodeType):
                traverse_code(instruction.argval)

    traverse_code(source_code)
    return dict(counts)
