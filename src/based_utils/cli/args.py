from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def check_integer(v: str, *, conditions: Callable[[int], bool] = None) -> int:
    value = int(v)
    if conditions and not conditions(value):
        raise ValueError(value)
    return value


def check_integer_within_range(
    low: int | None, high: int | None
) -> Callable[[str], int]:
    def is_in_within_range(n: int) -> bool:
        return (low is None or n >= low) and (high is None or n <= high)

    def check(v: str) -> int:
        return check_integer(v, conditions=is_in_within_range)

    return check
