import builtins
import dis
import types
import typing as tp


class Frame:
    """
    Frame header in cpython with description
        https://github.com/python/cpython/blob/3.12/Include/internal/pycore_frame.h

    Text description of frame parameters
        https://docs.python.org/3/library/inspect.html?highlight=frame#types-and-members
    """
    def __init__(self,
                 frame_code: types.CodeType,
                 frame_builtins: dict[str, tp.Any],
                 frame_globals: dict[str, tp.Any],
                 frame_locals: dict[str, tp.Any]) -> None:
        self.instructions_pointer = 0
        self.code = frame_code
        self.builtins = frame_builtins
        self.globals = frame_globals
        self.locals = frame_locals
        self.data_stack: tp.Any = []
        self.return_value = None
        self.kw_names = None

    kw_names: tp.Optional[str] = None

    def top(self) -> tp.Any:
        return self.data_stack[-1]

    def pop(self) -> tp.Any:
        return self.data_stack.pop()

    def push(self, *values: tp.Any) -> None:
        self.data_stack.extend(values)

    def popn(self, n: int) -> tp.Any:
        """
        Pop a number of values from the value stack.
        A list of n values is returned, the deepest value first.
        """
        if n > 0:
            returned = self.data_stack[-n:]
            self.data_stack[-n:] = []
            return returned
        else:
            return []

    def run(self, run: bool = True) -> tp.Any:
        self.instructions = list(dis.get_instructions(self.code))
        self.offset_instr_idx = {instructs.offset: idx
                                 for idx, instructs in enumerate(self.instructions)}

        while self.instructions_pointer < len(self.instructions):
            instruct = self.instructions[self.instructions_pointer]

            if run:
                getattr(self, instruct.opname.lower() + "_op")(instruct.arg, instruct.argval)
            self.instructions_pointer += 1

        return self.return_value

    def nop_op(self, arg: int, argval: int) -> tp.Any:
        pass

    def resume_op(self, arg: int, argval: int) -> tp.Any:
        pass

    def push_null_op(self, arg: int, argval: int) -> tp.Any:
        self.push(None)

    def precall_op(self, arg: int, argval: int) -> tp.Any:
        pass

    def call_op(self, arg: int, argval: int) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-CALL
        """
        kwargs = {}

        if self.kw_names is not None:
            list_kwargs = self.popn(len(self.kw_names))
            kwargs = dict(zip(self.kw_names, list_kwargs))

        args = self.popn(argval - len(kwargs))
        f = self.pop()

        var = self.pop() if self.data_stack else None
        res = var(f, *args, **kwargs) if var is not None else f(*args, **kwargs)

        self.push(res)
        self.kw_names = None

    def load_name_op(self, arg: int, argval: str) -> None:
        """
        Partial realization

        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-LOAD_NAME
        """
        match argval:
            case _ if argval in self.locals:
                self.push(self.locals[argval])
            case _ if argval in self.globals:
                self.push(self.globals[argval])
            case _ if argval in self.builtins:
                self.push(self.builtins[argval])
            case _:
                raise NameError()

    def load_global_op(self, arg: int, argval: str) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-LOAD_GLOBAL
        """
        if argval in self.builtins:
            self.push(self.builtins[argval])
        else:
            self.push(self.globals[argval])

    def load_const_op(self, arg: int, argval: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-LOAD_CONST
        """
        self.push(argval)

    def return_value_op(self, arg: int, argval: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-RETURN_VALUE
        """
        instr_len = len(self.instructions)
        self.return_value = self.pop()
        self.instructions_pointer = instr_len - 1

    def pop_top_op(self, arg: int, argval: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-POP_TOP
        """
        self.pop()

    def make_function_op(self, arg: int, argval: int) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-MAKE_FUNCTION
        """
        code = self.pop()  # the code associated with the function (at TOS1)

        defaults = []
        if argval & 0x01:
            defaults = self.pop()

        def f(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            parsed_args = {name: None for name in code.co_varnames}

            parsed_args.update({code.co_varnames[i + (code.co_argcount - len(defaults))]: defaults[i]
                                for i in range(len(defaults))})

            parsed_args.update(dict(zip(code.co_varnames, args), **kwargs))

            f_locals = {**self.locals, **parsed_args}

            frame = Frame(code, self.builtins, self.globals, f_locals)  # Run code in prepared environment
            return frame.run(True)

        self.push(f)

    def store_name_op(self, arg: str, argval: str) -> None:
        """
        Operation description:
            https://docs.python.org/release/3.12.5/library/dis.html#opcode-STORE_NAME
        """
        self.locals[argval] = self.pop()

    def copy_op(self, arg: int, argval: int) -> None:
        assert argval > 0

        self.push(self.data_stack[-argval])

    def import_name_op(self, arg: int, argval: str) -> None:
        module = __import__(argval, self.globals, self.locals, self.pop(), self.pop())

        self.push(module)

    def import_from_op(self, arg: int, argval: str) -> None:
        module = self.top()

        try:
            attr = getattr(module, argval)
        except AttributeError:
            raise ImportError(f"Cannot import name '{argval}' from '{module.__name__}'")

        self.push(attr)

    def call_intrinsic_1_op(self, arg: int, argval: int) -> None:
        var = self.pop()
        if hasattr(var, '__all__'):
            names = var.__all__
        else:
            names = []
            for name in dir(var):
                if not name.startswith('_'):
                    names.append(name)

        for name in names:
            self.locals[name] = getattr(var, name)

        if argval != 2:
            print(argval)
            assert False

        self.push(var)

    def load_fast_op(self, arg: int, argval: str) -> None:
        self.push(self.locals[argval])

    def load_fast_check_op(self, arg: int, argval: str) -> None:
        if argval in self.locals:
            self.push(self.locals[argval])
        else:
            raise UnboundLocalError(argval)

    def load_fast_and_clear_op(self, arg: int, argval: str) -> None:
        if argval in self.locals:
            self.push(self.locals[argval])
        else:
            self.push(None)

        self.locals[argval] = None

    def load_build_class_op(self, arg: int, argval: tp.Any) -> None:
        self.push(self.builtins['__build_class__'])

    def load_attr_op(self, arg: int, argval: str) -> None:
        obj = self.pop()

        if arg % 2 == 0:
            self.push(getattr(obj, argval))
        else:
            method = getattr(type(obj), argval, None)
            if callable(method):
                self.push(method)
                self.push(obj)
            else:
                self.push(None)
                self.push(getattr(self.pop(), argval))

    def swap_op(self, arg: int, argval: int) -> None:
        tmp = self.data_stack[-argval]
        self.data_stack[-argval] = self.data_stack[-1]
        self.data_stack[-1] = tmp

    def return_const_op(self, arg: int, argval: tp.Any) -> None:
        inst_len = len(self.instructions)
        self.return_value = argval
        self.instructions_pointer = inst_len - 1

    def store_global_op(self, arg: int, argval: str) -> None:
        glob = self.pop()
        self.globals[argval] = glob

    def store_fast_op(self, arg: int, argval: str) -> None:
        fast = self.pop()
        self.locals[argval] = fast

    def store_attr_op(self, arg: int, argval: str) -> None:
        obj = self.pop()
        val = self.pop()
        setattr(obj, argval, val)

    def store_subscr_op(self, arg: int, argval: None) -> None:
        key = self.pop()
        cont = self.pop()
        val = self.pop()
        cont[key] = val

    def build_tuple_op(self, arg: int, argval: int) -> None:
        if argval == 0:
            value = ()
        else:
            args = self.popn(argval)
            value = tuple(args)

        self.push(value)

    def build_list_op(self, arg: int, argval: int) -> None:
        if argval == 0:
            value = []
        else:
            args = self.popn(argval)
            value = list(args)

        self.push(value)

    def list_extend_op(self, arg: int, argval: int) -> None:
        seq = self.pop()
        self.data_stack[-argval].extend(seq)

    def list_append_op(self, arg: int, argval: int) -> None:
        seq = self.pop()
        self.data_stack[-argval].append(seq)

    def build_const_key_map_op(self, arg: int, argval: int) -> None:
        key = self.pop()
        values = [self.pop() for _ in range(argval)]
        res = dict(zip(reversed(key), values))

        self.push(res)

    def build_map_op(self, arg: int, argval: int) -> None:
        dictionary = {}
        for _ in range(argval):
            val = self.pop()
            key = self.pop()
            dictionary[key] = val

        self.push(dictionary)

    def map_add_op(self, arg: int, argval: int) -> None:
        val = self.pop()
        key = self.pop()
        dict.__setitem__(self.data_stack[-argval], key, val)

    def build_set_op(self, arg: int, argval: int) -> None:
        if argval == 0:
            value = set()
        else:
            args = self.popn(argval)
            value = set(args)

        self.push(value)

    def set_add_op(self, arg: int, argval: int) -> None:
        set.add(self.data_stack[-argval], self.pop())

    def build_string_op(self, arg: int, argval: int) -> None:
        if argval == 0:
            value = ''
        else:
            args = self.popn(argval)
            value = ''.join(args)

        self.push(value)

    def set_update_op(self, arg: int, argval: int) -> None:
        set.update(self.data_stack[-argval], self.pop())

    def store_slice_op(self, arg: int, argval: None) -> None:
        end = self.pop()
        start = self.pop()
        container = self.pop()
        val = self.pop()

        container[start:end] = val

    def unpack_sequence_op(self, arg: int, argval: int) -> None:
        val = self.pop()
        assert argval == len(val)

        for _ in val[::-1]:
            self.push(_)

    def format_value_op(self, arg: int, argval: tuple[tp.Any, ...]) -> None:
        if argval[1]:
            format_ = self.pop()
        else:
            format_ = ''

        val = self.pop()
        if argval[0] is not None:
            val = argval[0](val)

        formatted_val = format(val, format_)
        self.push(formatted_val)

    def binary_slice_op(self, arg: int, argval: None) -> None:
        end = self.pop()
        start = self.pop()
        container = self.pop()

        self.push(container[start:end])

    def build_slice_op(self, arg: int, argval: int) -> None:
        match argval:
            case 3:
                step = self.pop()
                end = self.pop()
                start = self.pop()
                self.push(slice(start, end, step))
            case 2:
                end = self.pop()
                start = self.pop()
                self.push(slice(start, end))
            case _:
                assert False

    def binary_subscr_op(self, arg: int, argval: tp.Any) -> None:
        key = self.pop()
        cont = self.pop()
        self.push(cont[key])

    def delete_name_op(self, arg: int, argval: tp.Optional[str]) -> None:
        match argval:
            case self.locals.get(argval):
                del self.locals[argval]
            case self.globals.get(argval):
                del self.globals[argval]

    def delete_fast_op(self, arg: int, argval: tp.Optional[str]) -> None:
        if argval in self.locals:
            del self.locals[argval]

    def delete_attr_op(self, arg: int, argval: tp.Optional[str]) -> None:
        if argval is not None:
            delattr(self.pop(), argval)

    def delete_subscr_op(self, arg: int, argval: None) -> None:
        key = self.pop()
        cont = self.pop()
        del cont[key]

    def unary_negative_op(self, arg: int, argval: int) -> None:
        self.push(-self.pop())

    def unary_not_op(self, arg: int, argval: int) -> None:
        self.push(not self.pop())

    def unary_invert_op(self, arg: int, argval: int) -> None:
        self.push(~self.pop())

    def binary_op_op(self, arg: int, argval: int) -> None:
        rhs = self.pop()
        lhs = self.pop()
        if argval < 13:
            argval = argval
        else:
            argval = argval - 13

        match argval:
            case 0:
                self.push(lhs + rhs)
            case 1:
                self.push(lhs & rhs)
            case 2:
                self.push(lhs // rhs)
            case 3:
                self.push(lhs << rhs)
            case 5:
                self.push(lhs * rhs)
            case 6:
                self.push(lhs % rhs)
            case 7:
                self.push(lhs | rhs)
            case 8:
                self.push(lhs ** rhs)
            case 9:
                self.push(lhs >> rhs)
            case 10:
                self.push(lhs - rhs)
            case 11:
                self.push(lhs / rhs)
            case 12:
                self.push(lhs ^ rhs)
            case _:
                print(f"Sorry, I couldn't understand {argval}")
                assert False

    def compare_op_op(self, arg: int, argval: str) -> None:
        rhs = self.pop()
        lhs = self.pop()
        match argval:
            case '==':
                self.push(lhs == rhs)
            case '!=':
                self.push(lhs != rhs)
            case '>':
                self.push(lhs > rhs)
            case '<':
                self.push(lhs < rhs)
            case '>=':
                self.push(lhs >= rhs)
            case '<=':
                self.push(lhs <= rhs)
            case _:
                print(f"Sorry, I couldn't understand {argval}")
                assert False

    def contains_op_op(self, arg: int, argval: str) -> None:
        rhs = self.pop()
        lhs = self.pop()
        if argval == 1:
            self.push(lhs not in rhs)
        else:
            self.push(lhs in rhs)

    def is_op_op(self, arg: int, argval: int) -> None:
        rhs = self.pop()
        lhs = self.pop()
        if argval == 1:
            self.push(lhs is not rhs)
        else:
            self.push(lhs is rhs)

    def pop_jump_if_none_op(self, arg: int, argval: int) -> None:
        val = self.pop()
        if not val:
            self.instructions_pointer = self.offset_instr_idx[argval] - 1

    def pop_jump_if_false_op(self, arg: int, argval: int) -> None:
        val = self.pop()
        if not bool(val):
            self.instructions_pointer = self.offset_instr_idx[argval] - 1

    def pop_jump_if_true_op(self, arg: int, argval: int) -> None:
        val = self.pop()
        if bool(val):
            self.instructions_pointer = self.offset_instr_idx[argval] - 1

    def jump_forward_op(self, arg: int, argval: int) -> None:
        self.instructions_pointer = self.offset_instr_idx[argval] - 1

    def jump_backward_op(self, arg: int, argval: int) -> None:
        self.instructions_pointer = self.offset_instr_idx[argval] - 1

    def get_iter_op(self, arg: int, argval: None) -> None:
        self.push(iter(self.pop()))

    def for_iter_op(self, arg: int, argval: int) -> None:
        try:
            self.push(next(self.top()))
        except StopIteration:
            self.push(None)
            self.instructions_pointer = (self.offset_instr_idx[argval] - 1)

    def end_for_op(self, arg: int, argval: int) -> None:
        self.popn(2)

    def kw_names_op(self, arg: int, argval: tp.Optional[str]) -> None:
        if argval is not None:
            self.kw_names = argval

    def load_assertion_error_op(self, arg: int, argval: tp.Any) -> None:
        self.push(AssertionError())

    def raise_varargs_op(self, arg: int, argval: int) -> None:
        match argval:
            case 0:
                raise
            case 1:
                rs = self.pop()
                raise rs
            case 2:
                r1 = self.pop()
                r2 = self.pop()
                raise r1 from r2
            case _:
                print(f"Sorry, I couldn't understand {argval}")
                assert False

    def reraise_op(self, arg: int, argval: int) -> None:
        raise self.pop()

    def setup_annotations_op(self, arg: int, argval: None) -> None:
        if '__annotations__' not in self.locals:
            self.locals['__annotations__'] = {}


class VirtualMachine:
    def run(self, code_obj: types.CodeType) -> None:
        """
        :param code_obj: code for interpreting
        """
        globals_context: dict[str, tp.Any] = {}
        frame = Frame(code_obj, builtins.globals()['__builtins__'], globals_context, globals_context)
        return frame.run()
