from functools import cached_property
from typing import TYPE_CHECKING

from .constants import FULL_CIRCLE

if TYPE_CHECKING:
    from collections.abc import Iterator


def frange(n: int, *, inclusive: bool = False) -> Iterator[float]:
    """
    Generate a range of n fractions from 0 to 1.

    :param n: amount of numbers generated
    :param inclusive: do we want to include 0 and 1 or not?
    :return: generated numbers

    >>> list(frange(0))
    []
    >>> list(frange(0, inclusive=True))
    [0, 1]
    >>> list(frange(1))
    [0.5]
    >>> list(frange(1, inclusive=True))
    [0, 0.5, 1]
    >>> list(frange(7))
    [0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
    >>> list(frange(7, inclusive=True))
    [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1]
    """
    end = n + 1
    if inclusive:
        yield 0
    for i in range(1, end):
        yield i / end
    if inclusive:
        yield 1


def trim(n: float, lower: float, upper: float) -> float:
    return min(max(lower, n), upper)


class Bounds:
    def __init__(self, begin: float, end: float) -> None:
        self._begin = begin
        self._end = end

    @cached_property
    def _span(self) -> float:
        return self._end - self._begin

    def interpolate(self, f: float) -> float:
        return self._begin + self._span * f

    def inverse_interpolate(self, n: float, *, inside: bool = True) -> float:
        try:
            f = (n - self._begin) / self._span
        except ZeroDivisionError:
            return 0.0
        return trim(f, 0.0, 1.0) if inside else f


class CyclicBounds(Bounds):
    def __init__(self, begin: float, end: float, period: float = None) -> None:
        period = period or FULL_CIRCLE
        begin, end = begin % period, end % period

        # To ensure interpolation over the smallest angle,
        # phase shift {begin} over whole periods, such that the
        # (absolute) difference between {begin} <-> {end} <= 1/2 {period}.
        #
        #                          v------ period ------v
        #    -1                    0                    1                    2
        #     |                    |                    |     begin < end:   |
        # Old:|                    |   B ~~~~~~~~~> E   |                    |
        # New:|                    |                E <~|~~ B' = B + period  |
        #     |    begin > end:    |                    |                    |
        # Old:|                    |   E <~~~~~~~~~ B   |                    |
        # New:|  B - period =  B'~~|~> E                |                    |

        if abs(end - begin) > period / 2:
            begin += period if begin < end else -period

        super().__init__(begin, end)
        self._period = period

    def interpolate(self, f: float) -> float:
        return super().interpolate(f) % self._period

    def inverse_interpolate(self, n: float, *, inside: bool = True) -> float:
        return super().inverse_interpolate(n % self._period, inside=inside)
