#!/usr/bin/env python3
import argparse
import ast
import operator
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from types import CodeType
from typing import Any, NoReturn


class InterpreterError(Exception):
    """Base exception class for errors raised by the intepreter."""


class CompilationError(InterpreterError):
    """Raised when a source is invalid or could not be compiled."""


class ExecutionError(InterpreterError):
    """Raised when a failure occurs in executing the program."""


class CycleLimitExceeded(ExecutionError):
    pass


@dataclass
class CycleContext:
    cycles: int = 0
    reads: int = 0
    writes: int = 0
    operations: int = 0
    max_cycles: int | None = None

    def charge_read(self) -> None:
        self.charge_cycle()
        self.reads += 1

    def charge_write(self) -> None:
        self.charge_cycle()
        self.writes += 1

    def charge_op(self) -> None:
        self.charge_cycle()
        self.operations += 1

    def charge_cycle(self) -> None:
        if self.max_cycles is not None and self.cycles >= self.max_cycles:
            raise CycleLimitExceeded(f'cycle limit exceeded ({self.max_cycles})')
        self.cycles += 1


class Value:
    __slots__ = ('value', 'ctx')

    def __init__(self, value: int, ctx: CycleContext) -> None:
        self.value = value
        self.ctx = ctx

    @staticmethod
    def _make_op(
        op,
        reflected: bool = False,
        wrap: bool = True,
        unary: bool = False,
    ):
        def meth(self: Any, other: Any) -> Any:
            self.ctx.charge_op()
            if unary:
                result = op(self.value)
            else:
                a = self.value
                b = other.value if isinstance(other, Value) else other
                if type(b) is not int:
                    raise TypeError(f'expected an integer, got {type(b).__name__!r}')
                if reflected:
                    a, b = b, a
                result = op(a, b)
            return Value(result, ctx=self.ctx) if wrap else result

        return meth

    __add__ = _make_op(operator.add)
    __radd__ = _make_op(operator.add, reflected=True)
    __sub__ = _make_op(operator.sub)
    __rsub__ = _make_op(operator.sub, reflected=True)
    __mul__ = _make_op(operator.mul)
    __rmul__ = _make_op(operator.mul, reflected=True)
    __floordiv__ = _make_op(operator.floordiv)
    __rfloordiv__ = _make_op(operator.floordiv, reflected=True)
    __mod__ = _make_op(operator.mod)
    __rmod__ = _make_op(operator.mod, reflected=True)
    __or__ = _make_op(operator.or_, reflected=True)
    __ror__ = _make_op(operator.or_, reflected=True)
    __xor__ = _make_op(operator.xor, reflected=True)
    __rxor__ = _make_op(operator.xor, reflected=True)
    __and__ = _make_op(operator.and_, reflected=True)
    __rand__ = _make_op(operator.and_, reflected=True)

    __eq__ = _make_op(operator.eq, wrap=False)
    __ne__ = _make_op(operator.ne, wrap=False)
    __lt__ = _make_op(operator.lt, wrap=False)
    __le__ = _make_op(operator.le, wrap=False)
    __gt__ = _make_op(operator.gt, wrap=False)
    __ge__ = _make_op(operator.ge, wrap=False)

    __neg__ = _make_op(operator.neg, unary=True)
    __pos__ = _make_op(operator.pos, unary=True)


class Memory:
    def __init__(self, size: int, *, max_cycles: int | None = None) -> None:
        self.data = [0] * size
        self.size = len(self.data)
        self.ctx = CycleContext(max_cycles=max_cycles)

    def _index(self, index: Any) -> int:
        if isinstance(index, Value):
            index = index.value
        if type(index) is not int:
            raise TypeError('memory index must be an integer')
        if not -self.size <= index < self.size:
            raise IndexError(f'memory index out of bounds: {index}')
        return index

    def _value(self, value: Any) -> int:
        if isinstance(value, Value):
            value = value.value
        if type(value) is not int:
            raise TypeError('memory value must be an integer')
        return value

    def set_value_at(self, index: Any, value: Any) -> None:
        index = self._index(index)
        value = self._value(value)
        self.data[index] = value

    def __getitem__(self, index: Any) -> Value:
        index = self._index(index)
        self.ctx.charge_read()
        return Value(self.data[index], ctx=self.ctx)

    def __setitem__(self, index: Any, value: Any) -> None:
        self.set_value_at(index, value)
        self.ctx.charge_write()


class Validator(ast.NodeVisitor):
    """AST validator for a tiny Python subset."""

    BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod, ast.BitOr, ast.BitXor, ast.BitAnd)
    UNARYOPS = (ast.UAdd, ast.USub)
    CMPOPS = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)

    def __init__(self, fn_arg: str) -> None:
        self.fn_arg = fn_arg

    def fail(self, node: ast.AST, message: str) -> NoReturn:
        raise CompilationError(f"{message} (at line {getattr(node, 'lineno', '?')})")

    def visit_function_body(self, fn: ast.FunctionDef) -> None:
        for stmt in fn.body:
            self.visit(stmt)

    def generic_visit(self, node: ast.AST) -> None:
        self.fail(node, f'forbidden syntax: {type(node).__name__.lower()!r}')

    def validate_memory_access(self, node: ast.AST, *, store: bool) -> None:
        if not isinstance(node, ast.Subscript):
            self.fail(node, 'assignment target must be a memory cell')

        expected_context = ast.Store if store else ast.Load
        if not isinstance(node.ctx, expected_context):
            self.fail(node, 'invalid memory access context')

        if not isinstance(node.value, ast.Name) or node.value.id != self.fn_arg:
            self.fail(node, 'target name does not match function parameter')

        if isinstance(node.slice, ast.Slice):
            self.fail(node, 'subscript cannot be a slice')

        self.visit(node.slice)

    def visit_Assign(self, node: ast.Assign) -> None:
        if len(node.targets) != 1:
            self.fail(node, 'cannot assign to multiple targets')
        self.validate_memory_access(node.targets[0], store=True)
        self.visit(node.value)

    def visit_If(self, node: ast.If) -> None:
        super().generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        super().generic_visit(node)

    def visit_Break(self, node: ast.Break) -> None:
        super().generic_visit(node)

    def visit_Continue(self, node: ast.Continue) -> None:
        super().generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if not isinstance(node.op, self.BINOPS):
            self.fail(node, 'forbidden arithmetic operator')
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if not isinstance(node.op, self.UNARYOPS):
            self.fail(node, 'forbidden unary operator')
        self.visit(node.operand)

    def visit_Compare(self, node: ast.Compare) -> None:
        if len(node.ops) != 1:
            self.fail(node, 'cannot use chained comparisons')
        if not isinstance(node.ops[0], self.CMPOPS):
            self.fail(node, 'forbidden comparison operator')
        self.visit(node.left)
        self.visit(node.comparators[0])

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self.validate_memory_access(node, store=False)

    def visit_Constant(self, node: ast.Constant) -> None:
        if type(node.value) is not int:
            self.fail(node, 'only integer constants are allowed')

    def visit_Name(self, node: ast.Name) -> None:
        self.fail(node, 'bare names are forbidden')


def validate_source(tree: ast.AST, visit: bool = True) -> tuple[ast.Module, str]:
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise CompilationError('program must define exactly one top-level function')

    fn = tree.body[0]

    if fn.decorator_list:
        raise CompilationError('decorators are forbidden')
    if fn.returns or fn.type_params:
        raise CompilationError('function annotations are forbidden')

    args = fn.args
    if (
        len(args.args) != 1 or
        args.posonlyargs or
        args.kwonlyargs or
        args.vararg or
        args.kwarg or
        args.defaults or
        args.kw_defaults
    ):
        raise CompilationError('function must take one parameter')

    param = args.args[0]
    if param.annotation:
        raise CompilationError('parameter annotations are forbidden')

    if '__' in fn.name or '__' in param.arg:
        raise CompilationError('dunder names are forbidden in function signature')

    if visit:
        Validator(param.arg).visit_function_body(fn)

    return fn.name


class Interpreter:
    def __init__(
        self,
        *,
        memory_size: int,
        max_cycles: int | None = None,
        validate: bool = True,
    ) -> None:
        self.memory_size = memory_size
        self.max_cycles = max_cycles
        self.validate = validate

    def _compile(self, source: str) -> tuple[CodeType, str]:
        try:
            tree = ast.parse(source, mode='exec')
        except SyntaxError as exc:
            raise CompilationError(
                f'syntax error at line {exc.lineno}: {exc.msg}'
            ) from exc

        func_name = validate_source(tree, self.validate)
        return compile(tree, '<string>', 'exec'), func_name

    def run(self, source: str, initial_memory: Sequence[int] | None = None) -> Memory:
        code, func_name = self._compile(source)
        namespace: dict[str, Any] = {}
        try:
            exec(code, namespace, namespace)
        except Exception as exc:
            raise ExecutionError('could not execute source') from exc

        func = namespace.get(func_name)
        if func is None or not callable(func):
            raise ExecutionError('compiled function is missing')

        memory = Memory(self.memory_size, max_cycles=self.max_cycles)
        if initial_memory is not None:
            for index in range(len(initial_memory)):
                memory.set_value_at(index, initial_memory[index])

        result = func(memory)
        if result is not None:
            raise ExecutionError('function must not return a value')

        return memory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('-m', '--memory-size', type=int, default=4096)
    parser.add_argument('-c', '--max-cycles', type=int, default=1_000_000)
    parser.add_argument('-V', '--no-validate', dest='validate', action='store_false')

    args = parser.parse_args()

    with open(args.filename, 'r') as f:
        submission = f.read()

    interpreter = Interpreter(
        memory_size=args.memory_size,
        max_cycles=args.max_cycles,
        validate=args.validate,
    )
    memory = interpreter.run(submission)

    print('--- statistics ---')
    print(f'total cycles: {memory.ctx.cycles}')
    print(f'memory reads: {memory.ctx.reads}')
    print(f'memory writes: {memory.ctx.writes}')
    print(f'operations: {memory.ctx.operations}')


if __name__ == '__main__':
    try:
        main()
    except CompilationError as exc:
        print(f'\x1b[1;31mcompile error:\x1b[0m {exc}', file=sys.stderr)
    except ExecutionError as exc:
        print(f'\x1b[1;31mexecution error:\x1b[0m {exc}', file=sys.stderr)
    except Exception as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
