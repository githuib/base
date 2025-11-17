from functools import cached_property
from math import isclose
from typing import TYPE_CHECKING

from .constants import FULL_CIRCLE

if TYPE_CHECKING:
    from collections.abc import Iterator


def trim(n: float, lower: float = 0, upper: float = 1) -> float:
    return min(max(lower, n), upper)


class InterpolationBounds:
    def __init__(self, begin: float = 0, end: float = 1) -> None:
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


class CyclicInterpolationBounds(InterpolationBounds):
    def __init__(
        self, begin: float = 0, end: float = None, period: float = None
    ) -> None:
        if end is None:
            end = FULL_CIRCLE
        if period is None:
            period = FULL_CIRCLE
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


def interpolate(f: float, *, begin: float = 0, end: float = 1) -> float:
    bounds = InterpolationBounds(begin, end)
    return bounds.interpolate(f)


def inverse_interpolate(
    n: float, *, begin: float = 0, end: float = 1, inside: bool = True
) -> float:
    bounds = InterpolationBounds(begin, end)
    return bounds.inverse_interpolate(n, inside=inside)


def interpolate_cyclic(
    f: float, *, begin: float = 0, end: float = None, period: float = None
) -> float:
    bounds = CyclicInterpolationBounds(begin, end, period)
    return bounds.interpolate(f)


def inverse_interpolate_cyclic(
    n: float,
    *,
    begin: float = 0,
    end: float = None,
    period: float = None,
    inside: bool = True,
) -> float:
    bounds = CyclicInterpolationBounds(begin, end, period)
    return bounds.inverse_interpolate(n, inside=inside)


def interpolate_angle(f: float, *, angle_1: float = 0, angle_2: float = None) -> float:
    bounds = CyclicInterpolationBounds(angle_1, angle_2, FULL_CIRCLE)
    return bounds.interpolate(f)


def inverse_interpolate_angle(
    n: float, *, angle_1: float = 0, angle_2: float = None, inside: bool = True
) -> float:
    bounds = CyclicInterpolationBounds(angle_1, angle_2, FULL_CIRCLE)
    return bounds.inverse_interpolate(n, inside=inside)


def frange(
    step: float,
    start_or_end: float = None,
    end: float = None,
    *,
    inclusive: bool = False,
) -> Iterator[float]:
    """
    Generate a range of numbers within the given range increasing with the given step.

    :param step: difference between two successive numbers in the range
    :param start_or_end: start of range (or end of range, if end not given)
    :param end: end of range
    :param inclusive: do we want to include 0 and 1 or not?
    :return: generated numbers

    >>> " ".join(f"{n:.2f}" for n in frange(0))
    Traceback (most recent call last):
    ...
    ValueError: 0
    >>> " ".join(f"{n:.2f}" for n in frange(0, inclusive=True))
    Traceback (most recent call last):
    ...
    ValueError: 0
    >>> " ".join(f"{n:.3f}" for n in frange(1))
    ''
    >>> " ".join(f"{n:.3f}" for n in frange(1, inclusive=True))
    '0.000 1.000'
    >>> " ".join(f"{n:.3f}" for n in frange(0.125))
    '0.125 0.250 0.375 0.500 0.625 0.750 0.875'
    >>> " ".join(f"{n:.3f}" for n in frange(0.125, inclusive=True))
    '0.000 0.125 0.250 0.375 0.500 0.625 0.750 0.875 1.000'
    >>> " ".join(f"{n:.2f}" for n in frange(0.12))
    '0.12 0.24 0.36 0.48 0.60 0.72 0.84 0.96'
    >>> " ".join(f"{n:.2f}" for n in frange(0.12, inclusive=True))
    '0.00 0.12 0.24 0.36 0.48 0.60 0.72 0.84 0.96 1.00'
    >>> " ".join(f"{n:.2f}" for n in frange(0.13))
    '0.13 0.26 0.39 0.52 0.65 0.78 0.91'
    >>> " ".join(f"{n:.2f}" for n in frange(0.13, inclusive=True))
    '0.00 0.13 0.26 0.39 0.52 0.65 0.78 0.91 1.00'
    >>> " ".join(f"{n:.2f}" for n in frange(0.13, 0.51))
    '0.13 0.26 0.39'
    >>> " ".join(f"{n:.2f}" for n in frange(0.13, 0.52))
    '0.13 0.26 0.39'
    >>> " ".join(f"{n:.2f}" for n in frange(0.13, 0.53))
    '0.13 0.26 0.39 0.52'
    >>> " ".join(f"{n:.2f}" for n in frange(1.13, -3.4, 4.50))
    '-2.27 -1.14 -0.01 1.12 2.25 3.38'
    >>> " ".join(f"{n:.2f}" for n in frange(1.13, -3.4, 4.51))
    '-2.27 -1.14 -0.01 1.12 2.25 3.38'
    >>> " ".join(f"{n:.2f}" for n in frange(1.13, -3.4, 4.52))
    '-2.27 -1.14 -0.01 1.12 2.25 3.38 4.51'
    """
    if not step:
        raise ValueError(step)
    s: float
    e: float
    if end is None:
        s, e = 0, start_or_end or 1
    else:
        s, e = start_or_end or 0, end

    if inclusive:
        yield s
    n = s + step
    while n < e and not isclose(n, e):
        yield n
        n += step
    if inclusive:
        yield e


def fractions(n: int, *, inclusive: bool = False) -> Iterator[float]:
    """
    Generate a range of n fractions from 0 to 1.

    :param n: amount of numbers generated
    :param inclusive: do we want to include 0 and 1 or not?
    :return: generated numbers

    >>> " ".join(f"{n:.3f}" for n in fractions(0))
    ''
    >>> " ".join(f"{n:.3f}" for n in fractions(0, inclusive=True))
    '0.000 1.000'
    >>> " ".join(f"{n:.3f}" for n in fractions(1))
    '0.500'
    >>> " ".join(f"{n:.3f}" for n in fractions(1, inclusive=True))
    '0.000 0.500 1.000'
    >>> " ".join(f"{n:.3f}" for n in fractions(7))
    '0.125 0.250 0.375 0.500 0.625 0.750 0.875'
    >>> " ".join(f"{n:.3f}" for n in fractions(7, inclusive=True))
    '0.000 0.125 0.250 0.375 0.500 0.625 0.750 0.875 1.000'
    """
    return frange(1 / (n + 1), inclusive=inclusive)
