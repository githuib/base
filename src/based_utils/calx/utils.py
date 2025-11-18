import cmath
import math
from secrets import randbelow


def randf(exclusive_upper_bound: float = 1, precision: int = 8) -> float:
    epb = 10 ** (math.ceil(math.log10(exclusive_upper_bound)) + precision)
    return randbelow(epb) * exclusive_upper_bound / epb


def solve_quadratic(a: float, b: float, c: float) -> tuple[float, float]:
    """
    Find x where ax^2 + bx + c = 0.

    >>> solve_quadratic(20.6, -10.3, 8.7)
    (0.25, 0.25)
    >>> solve_quadratic(2.5, 25.0, 20.0)
    (-9.12310562561766, -0.8768943743823392)
    """
    r = cmath.sqrt(b**2 - 4 * a * c).real

    def root(f: int) -> float:
        return (-b + r * f) / (2 * a)

    left, right = sorted([root(-1), root(1)])
    return left, right


def mods(x: int, y: int, shift: int = 0) -> int:
    return (x - shift) % y + shift


def compare(v1: int, v2: int) -> int:
    return (v1 < v2) - (v1 > v2)
