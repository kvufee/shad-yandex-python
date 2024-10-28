from contextlib import contextmanager
from typing import Iterator, Type, TextIO
import sys
import traceback


@contextmanager
def supresser(*types_: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except types_:
        pass


@contextmanager
def retyper(type_from: Type[BaseException], type_to: Type[BaseException]) -> Iterator[None]:
    try:
        yield
    except type_from as e:
        raise type_to(*e.args).with_traceback(e.__traceback__)


@contextmanager
def dumper(stream: TextIO | None = None) -> Iterator[None]:
    if stream is None:
        stream = sys.stderr

    try:
        yield
    except BaseException as e:
        formatted_exception = f"{traceback.format_exception_only(type(e), e)}"
        stream.write(formatted_exception)
        raise
