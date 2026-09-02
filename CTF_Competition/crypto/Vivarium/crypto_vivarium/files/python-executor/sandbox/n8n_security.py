"""n8n-compatible Python task validation and execution helpers.

The validation rules and runtime guards in this module intentionally track the
current n8n Python task runner at commit
bcbea0ab6c38e05654f2cd626bc14b320470467d.
"""

import ast
import builtins
import collections
import importlib
import re
import string
import sys


ALLOWED_MODULES = frozenset()
EXTERNAL_MODULES = frozenset()

DENIED_BUILTINS = frozenset(
    {
        "__build_class__",
        "breakpoint",
        "compile",
        "copyright",
        "credits",
        "delattr",
        "dir",
        "eval",
        "exec",
        "getattr",
        "globals",
        "hasattr",
        "help",
        "input",
        "license",
        "locals",
        "memoryview",
        "object",
        "open",
        "setattr",
        "type",
        "vars",
    }
)

SAFE_FORMAT_KEY = "__n8n_internal_safe_format__"
FORMAT_METHOD_NAMES = frozenset({"format", "format_map", "get_field", "vformat"})
BLOCKED_NAMES = frozenset(
    {
        "__loader__",
        "__builtins__",
        "__globals__",
        "__spec__",
        "__name__",
        SAFE_FORMAT_KEY,
    }
)
BLOCKED_ATTRIBUTES = frozenset(
    {
        "__subclasses__",
        "__globals__",
        "__builtins__",
        "__traceback__",
        "tb_frame",
        "tb_next",
        "f_back",
        "f_globals",
        "f_locals",
        "f_code",
        "f_builtins",
        "__getattribute__",
        "__qualname__",
        "__module__",
        "gi_frame",
        "gi_code",
        "gi_yieldfrom",
        "cr_frame",
        "cr_code",
        "ag_frame",
        "ag_code",
        "obj",
        "__thisclass__",
        "__self_class__",
        "__objclass__",
        "__reduce__",
        "__reduce_ex__",
        "__prepare__",
        "__instancecheck__",
        "__subclasscheck__",
        "__match_args__",
        "__base__",
        "__class__",
        "__bases__",
        "__code__",
        "__closure__",
        "__loader__",
        "__cached__",
        "__dict__",
        "__import__",
        "__mro__",
        "__init_subclass__",
        "__getattr__",
        "__setattr__",
        "__delattr__",
        "__self__",
        "__func__",
        "__wrapped__",
        "__annotations__",
        "__spec__",
    }
)

ERROR_RELATIVE_IMPORT = "Relative imports are disallowed."
ERROR_STDLIB_DISALLOWED = (
    "Import of standard library module '{module}' is disallowed. "
    "Allowed stdlib modules: {allowed}"
)
ERROR_EXTERNAL_DISALLOWED = (
    "Import of external package '{module}' is disallowed. "
    "Allowed external packages: {allowed}"
)
ERROR_DANGEROUS_NAME = (
    "Access to name '{name}' is disallowed, because it can be used to bypass "
    "security restrictions."
)
ERROR_DANGEROUS_ATTRIBUTE = (
    "Access to attribute '{attr}' is disallowed, because it can be used to "
    "bypass security restrictions."
)
ERROR_DANGEROUS_STRING_PATTERN = (
    "String pattern accessing '{attr}' is disallowed, because it can be used "
    "to bypass security restrictions."
)
ERROR_NAME_MANGLED_ATTRIBUTE = (
    "Access to name-mangled attributes (pattern: _ClassName__attr) is "
    "disallowed for security reasons."
)
ERROR_DYNAMIC_IMPORT = "Dynamic __import__() calls are not allowed for security reasons."
ERROR_MATCH_PATTERN_ATTRIBUTE = (
    "Match pattern extracting attribute '{attr}' is disallowed, because it "
    "can be used to bypass security restrictions."
)
ERROR_MATCH_POSITIONAL_PATTERN = (
    "Positional match patterns are disallowed for security reasons."
)
ERROR_GLOBAL_BLOCKED_NAME = (
    "Global declaration of '{name}' is disallowed, because it can be used to "
    "bypass security restrictions."
)
ERROR_FUNCDEF_BLOCKED_NAME = "Function named '{name}' is disallowed, because it can be used to bypass security restrictions."
ERROR_CLASSDEF_BLOCKED_NAME = "Class named '{name}' is disallowed, because it can be used to bypass security restrictions."
ERROR_PARAM_BLOCKED_NAME = "Parameter named '{name}' is disallowed, because it can be used to bypass security restrictions."
ERROR_BARE_FORMAT_ATTRIBUTE = (
    "Extracting '{attr}' as a bound method is disallowed; call it directly on "
    "its receiver instead."
)


class SecurityViolationError(Exception):
    def __init__(self, message, description=""):
        super().__init__(message)
        self.description = description


def validate_module_import(module_path, importing_package=None):
    if module_path.startswith(".") and importing_package:
        try:
            module_path = importlib.util.resolve_name(module_path, importing_package)
        except (ImportError, ValueError):
            pass

    module_name = module_path.split(".")[0]
    is_stdlib = module_name in sys.stdlib_module_names
    if is_stdlib and module_name in ALLOWED_MODULES:
        return True, None
    if not is_stdlib and module_name in EXTERNAL_MODULES:
        return True, None

    if is_stdlib:
        allowed = ", ".join(sorted(ALLOWED_MODULES)) if ALLOWED_MODULES else "none"
        return False, ERROR_STDLIB_DISALLOWED.format(
            module=module_path, allowed=allowed
        )

    allowed = ", ".join(sorted(EXTERNAL_MODULES)) if EXTERNAL_MODULES else "none"
    return False, ERROR_EXTERNAL_DISALLOWED.format(
        module=module_path, allowed=allowed
    )


_FORMATTER = string.Formatter()
_FIELD_ATTR_PATTERN = re.compile(r"\.(\w+)")
_FIELD_SUBSCRIPT_PATTERN = re.compile(r"\[(['\"]?)(\w+)\1\]")


def find_blocked_format_tokens(template):
    try:
        parsed = list(_FORMATTER.parse(template))
    except (ValueError, IndexError):
        return

    for _literal, field_name, format_spec, _conversion in parsed:
        if field_name is not None:
            for attr_match in _FIELD_ATTR_PATTERN.finditer(field_name):
                attr = attr_match.group(1)
                if attr in BLOCKED_ATTRIBUTES or attr in BLOCKED_NAMES:
                    yield attr

            for subscript_match in _FIELD_SUBSCRIPT_PATTERN.finditer(field_name):
                key = subscript_match.group(2)
                if key in BLOCKED_ATTRIBUTES or key in BLOCKED_NAMES:
                    yield key

        if format_spec:
            yield from find_blocked_format_tokens(format_spec)


class SecurityValidator(ast.NodeVisitor):
    def __init__(self):
        self.checked_modules = set()
        self.violations = []
        self._call_func_attr_ids = set()

    def visit_Import(self, node):
        for alias in node.names:
            self._validate_import(alias.name, node.lineno)
            if alias.asname and alias.asname in BLOCKED_NAMES:
                self._add_violation(
                    node.lineno, ERROR_DANGEROUS_NAME.format(name=alias.asname)
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.level > 0:
            self._add_violation(node.lineno, ERROR_RELATIVE_IMPORT)
        elif node.module:
            self._validate_import(node.module, node.lineno)

        for alias in node.names:
            if alias.asname and alias.asname in BLOCKED_NAMES:
                self._add_violation(
                    node.lineno, ERROR_DANGEROUS_NAME.format(name=alias.asname)
                )
            elif alias.name in BLOCKED_NAMES:
                self._add_violation(
                    node.lineno, ERROR_DANGEROUS_NAME.format(name=alias.name)
                )
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in BLOCKED_NAMES:
            self._add_violation(
                node.lineno, ERROR_DANGEROUS_NAME.format(name=node.id)
            )
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr in BLOCKED_ATTRIBUTES:
            self._add_violation(
                node.lineno, ERROR_DANGEROUS_ATTRIBUTE.format(attr=node.attr)
            )

        if (
            node.attr in FORMAT_METHOD_NAMES
            and id(node) not in self._call_func_attr_ids
        ):
            self._add_violation(
                node.lineno, ERROR_BARE_FORMAT_ATTRIBUTE.format(attr=node.attr)
            )

        if node.attr.startswith("_") and "__" in node.attr:
            parts = node.attr.split("__", 1)
            if len(parts) == 2 and parts[0].startswith("_"):
                self._add_violation(node.lineno, ERROR_NAME_MANGLED_ATTRIBUTE)
        self.generic_visit(node)

    def visit_Call(self, node):
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in FORMAT_METHOD_NAMES
        ):
            self._call_func_attr_ids.add(id(node.func))

        is_import_call = (
            isinstance(node.func, ast.Name) and node.func.id == "__import__"
        ) or (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "__import__"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in {"builtins", "__builtins__"}
        )
        if is_import_call:
            if (
                node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                self._validate_import(node.args[0].value, node.lineno)
            else:
                self._add_violation(node.lineno, ERROR_DYNAMIC_IMPORT)
        self.generic_visit(node)

    def visit_Subscript(self, node):
        is_builtins_access = (
            isinstance(node.value, ast.Name)
            and node.value.id in {"__builtins__", "builtins"}
        ) or (
            isinstance(node.value, ast.Attribute)
            and node.value.attr in {"__builtins__", "builtins"}
        )
        if (
            is_builtins_access
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
            and node.slice.value in BLOCKED_ATTRIBUTES
        ):
            self._add_violation(
                node.lineno,
                ERROR_DANGEROUS_ATTRIBUTE.format(attr=node.slice.value),
            )
        self.generic_visit(node)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self._scan_string_literal(node.value, node.lineno)
        self.generic_visit(node)

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            assembled = self._try_assemble_string_concat(node)
            if assembled is not None:
                self._scan_string_literal(assembled, node.lineno)
        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            if name in BLOCKED_NAMES:
                self._add_violation(
                    node.lineno, ERROR_GLOBAL_BLOCKED_NAME.format(name=name)
                )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name in BLOCKED_NAMES:
            self._add_violation(
                node.lineno, ERROR_FUNCDEF_BLOCKED_NAME.format(name=node.name)
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if node.name in BLOCKED_NAMES:
            self._add_violation(
                node.lineno, ERROR_FUNCDEF_BLOCKED_NAME.format(name=node.name)
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if node.name in BLOCKED_NAMES:
            self._add_violation(
                node.lineno, ERROR_CLASSDEF_BLOCKED_NAME.format(name=node.name)
            )
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.name and node.name in BLOCKED_NAMES:
            self._add_violation(
                node.lineno, ERROR_DANGEROUS_NAME.format(name=node.name)
            )
        self.generic_visit(node)

    def visit_arg(self, node):
        if node.arg in BLOCKED_NAMES:
            self._add_violation(
                node.lineno, ERROR_PARAM_BLOCKED_NAME.format(name=node.arg)
            )
        self.generic_visit(node)

    def visit_MatchClass(self, node):
        if node.patterns:
            self._add_violation(node.lineno, ERROR_MATCH_POSITIONAL_PATTERN)
        for attr in node.kwd_attrs:
            if attr in BLOCKED_ATTRIBUTES:
                self._add_violation(
                    node.lineno, ERROR_MATCH_PATTERN_ATTRIBUTE.format(attr=attr)
                )
        self.generic_visit(node)

    def _scan_string_literal(self, value, lineno):
        if value in BLOCKED_NAMES:
            self._add_violation(
                lineno, ERROR_DANGEROUS_NAME.format(name=value)
            )
            return
        if value in BLOCKED_ATTRIBUTES:
            self._add_violation(
                lineno, ERROR_DANGEROUS_ATTRIBUTE.format(attr=value)
            )
            return
        for token in find_blocked_format_tokens(value):
            self._add_violation(
                lineno, ERROR_DANGEROUS_STRING_PATTERN.format(attr=token)
            )

    def _try_assemble_string_concat(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._try_assemble_string_concat(node.left)
            if left is None:
                return None
            right = self._try_assemble_string_concat(node.right)
            if right is None:
                return None
            return left + right
        return None

    def _validate_import(self, module_path, lineno):
        if module_path.startswith("."):
            self._add_violation(lineno, ERROR_RELATIVE_IMPORT)
            return
        module_name = module_path.split(".")[0]
        if module_name in self.checked_modules:
            return
        self.checked_modules.add(module_name)
        is_allowed, error = validate_module_import(module_path)
        if not is_allowed:
            self._add_violation(lineno, error)

    def _add_violation(self, lineno, message):
        self.violations.append(f"Line {lineno}: {message}")


def validate_user_code(source):
    tree = ast.parse(source)
    validator = SecurityValidator()
    validator.visit(tree)
    if validator.violations:
        raise SecurityViolationError(
            "Security violations detected",
            "\n".join(validator.violations),
        )


class FormatGuardTransformer(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in FORMAT_METHOD_NAMES
        ):
            replacement = ast.Call(
                func=ast.Name(id=SAFE_FORMAT_KEY, ctx=ast.Load()),
                args=[
                    ast.Constant(value=node.func.attr),
                    node.func.value,
                    *node.args,
                ],
                keywords=node.keywords,
            )
            return ast.copy_location(replacement, node)
        return node


def _validate_format_template(template):
    token = next(find_blocked_format_tokens(template), None)
    if token is not None:
        raise SecurityViolationError(
            "Security violation detected",
            ERROR_DANGEROUS_STRING_PATTERN.format(attr=token),
        )


def _validate_field_expression(expression):
    _validate_format_template("{" + expression + "}")


_TEMPLATE_METHODS = frozenset({"format", "format_map", "vformat"})
_FIELD_METHODS = frozenset({"get_field"})


def _resolve_template_arg(method_name, receiver, args):
    is_template = method_name in _TEMPLATE_METHODS
    is_field = method_name in _FIELD_METHODS
    if not is_template and not is_field:
        return None, None

    if is_template:
        if isinstance(receiver, str):
            return receiver, None
        if isinstance(receiver, collections.UserString):
            return receiver.data, None

    if isinstance(receiver, type):
        if issubclass(receiver, str):
            candidate = args[0] if args else None
        elif issubclass(receiver, collections.UserString) and is_template:
            instance = args[0] if args else None
            candidate = (
                instance.data
                if isinstance(instance, collections.UserString)
                else None
            )
        else:
            candidate = args[1] if len(args) >= 2 else None
    else:
        candidate = args[0] if args else None

    if not isinstance(candidate, str):
        return None, None
    if is_field:
        return None, candidate
    return candidate, None


def _safe_format_impl(method_name, receiver, *args, **kwargs):
    template, field = _resolve_template_arg(method_name, receiver, args)
    if template is not None:
        _validate_format_template(template)
    if field is not None:
        _validate_field_expression(field)
    return getattr(receiver, method_name)(*args, **kwargs)


_INTROSPECTION_DENY = BLOCKED_ATTRIBUTES | frozenset(
    {
        "__call__",
        "__init__",
        "__new__",
        "__doc__",
        "__dir__",
        "__subclasshook__",
        "__repr__",
    }
)


class _HardenedCallable:
    __slots__ = ()
    _DENY = _INTROSPECTION_DENY

    def __getattribute__(self, name):
        if name in object.__getattribute__(type(self), "_DENY"):
            raise AttributeError(name)
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        raise AttributeError(name)

    def __delattr__(self, name):
        raise AttributeError(name)


class _SafeFormat(_HardenedCallable):
    __slots__ = ("_impl",)
    _DENY = _INTROSPECTION_DENY | frozenset({"_impl"})

    def __init__(self, implementation):
        object.__setattr__(self, "_impl", implementation)

    def __call__(self, method_name, receiver, *args, **kwargs):
        implementation = object.__getattribute__(self, "_impl")
        return implementation(method_name, receiver, *args, **kwargs)

    def __repr__(self):
        return ""


def _import_module_anchor(args, kwargs):
    package = kwargs.get("package")
    if isinstance(package, str):
        return package
    if args and isinstance(args[0], str):
        return args[0]
    return None


def _level_relative_target(name, args, kwargs):
    if not isinstance(name, str):
        return None
    level = kwargs.get("level")
    if level is None and len(args) >= 4:
        level = args[3]
    if not isinstance(level, int) or level <= 0:
        return None
    importer_globals = kwargs.get("globals")
    if importer_globals is None and args and isinstance(args[0], dict):
        importer_globals = args[0]
    if not isinstance(importer_globals, dict):
        return None
    anchor = importer_globals.get("__package__")
    if not isinstance(anchor, str) or not anchor:
        return None
    return "." * level + name, anchor


def _validation_target(name, args, kwargs):
    anchor = _import_module_anchor(args, kwargs)
    if anchor is not None:
        return name, anchor
    relative = _level_relative_target(name, args, kwargs)
    if relative is not None:
        return relative
    return name, None


class _GuardedImport(_HardenedCallable):
    __slots__ = ("_original",)
    _DENY = _INTROSPECTION_DENY | frozenset({"_original"})

    def __init__(self, original):
        object.__setattr__(self, "_original", original)

    def __call__(self, name, *args, **kwargs):
        check_name, package = _validation_target(name, args, kwargs)
        is_allowed, error = validate_module_import(check_name, package)
        if not is_allowed:
            raise SecurityViolationError("Security violation detected", error)
        original = object.__getattribute__(self, "_original")
        return original(name, *args, **kwargs)

    def __repr__(self):
        return ""


class _ImmutableBuiltins:
    __slots__ = ("_values",)

    def __init__(self, values):
        object.__setattr__(self, "_values", values)

    def __getitem__(self, key):
        return object.__getattribute__(self, "_values")[key]

    def __contains__(self, key):
        return key in object.__getattribute__(self, "_values")

    def __iter__(self):
        return iter(object.__getattribute__(self, "_values"))

    def __len__(self):
        return len(object.__getattribute__(self, "_values"))

    def keys(self):
        return object.__getattribute__(self, "_values").keys()

    def values(self):
        return object.__getattribute__(self, "_values").values()

    def items(self):
        return object.__getattribute__(self, "_values").items()

    def get(self, key, default=None):
        return object.__getattribute__(self, "_values").get(key, default)

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, "_values")[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name, value):
        raise AttributeError("read-only")

    def __delattr__(self, name):
        raise AttributeError("read-only")

    def __repr__(self):
        values = object.__getattribute__(self, "_values")
        return f"ImmutableBuiltins({len(values)} keys)"


_PRISTINE_IMPORT_MODULE = importlib.import_module
_PRISTINE_DUNDER_IMPORT = importlib.__import__
SAFE_FORMAT = _SafeFormat(_safe_format_impl)


def compile_user_code(source):
    validate_user_code(source)
    tree = ast.parse(source, "<specimen>", "exec")
    tree = FormatGuardTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    return compile(tree, "<specimen>", "exec")


def safe_builtins():
    filtered = {
        name: value
        for name, value in vars(builtins).items()
        if name not in DENIED_BUILTINS
    }
    filtered["__import__"] = _GuardedImport(builtins.__import__)
    return _ImmutableBuiltins(filtered)


def sanitize_sys_modules():
    safe_modules = {
        "builtins",
        "__main__",
        "sys",
        "traceback",
        "linecache",
        "importlib",
        "importlib.machinery",
        *ALLOWED_MODULES,
    }
    safe_prefixes = [name + "." for name in safe_modules]
    to_remove = [
        name
        for name in sys.modules
        if name not in safe_modules
        and not any(name.startswith(prefix) for prefix in safe_prefixes)
    ]
    for name in to_remove:
        del sys.modules[name]


def harden_importlib():
    importlib.import_module = _GuardedImport(_PRISTINE_IMPORT_MODULE)
    importlib.__import__ = _GuardedImport(_PRISTINE_DUNDER_IMPORT)
