from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from yachalk import chalk

from based_utils.calx import fractions
from based_utils.colors import Color, colors

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class Colored:
    value: object
    color: Color | None = None
    background: Color | None = None

    def with_color(self, color: Color) -> Colored:
        return Colored(self.value, color, self.background)

    def with_background(self, background: Color) -> Colored:
        return Colored(self.value, self.color, background)

    @cached_property
    def formatted(self) -> str:
        s = str(self.value)
        if self.color:
            s = chalk.hex(self.color.hex)(s)
        if self.background:
            s = chalk.bg_hex(self.background.hex)(s)
        return s

    def __repr__(self) -> str:
        return self.formatted

    def __str__(self) -> str:
        return self.formatted


def color_shades(c: Color) -> Iterator[str]:
    for f in fractions(9):
        s = c.shade(f)
        yield Colored(f" {f * 100:.0f}% ", s.contrasting_shade, s).formatted


def color_line(c: Color, n: str = "") -> str:
    h = "   " if n == "grey" else f"{c.hue * 360:03.0f}"
    return "".join(color_shades(c)) + Colored(f" {h} {n}", c).formatted


def saturation_lines(saturation: float) -> Iterator[str]:
    if saturation == 0:
        yield color_line(Color.grey(), "grey")
    else:
        yield ""
        for h in colors:
            yield color_line(Color.from_name(h, saturation=saturation), h)


def color_lines() -> Iterator[str]:
    for saturation in fractions(3, inclusive=True):
        yield from saturation_lines(saturation)
