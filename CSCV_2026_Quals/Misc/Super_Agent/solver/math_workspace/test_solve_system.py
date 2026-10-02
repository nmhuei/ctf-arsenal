import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOLVER = ROOT / "solve_system.py"


def load_solver():
    spec = importlib.util.spec_from_file_location("solve_system", SOLVER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_candidate_operator_set_covers_declared_families():
    solver = load_solver()

    names = {op.name for op in solver.candidate_operators()}

    assert {"add", "sub", "rsub", "xor", "rol", "ror", "mul", "not", "swap_nibbles"} <= names


def test_enumerated_solutions_reproduce_all_observations():
    solver = load_solver()

    solutions = solver.enumerate_solutions()

    assert solutions
    for solution in solutions:
        observed = solver.apply_mapping(solution["operators"], solver.VECTOR_X)
        assert observed == solver.VECTOR_Y
        assert solution["matched"] == len(solver.VECTOR_X)
