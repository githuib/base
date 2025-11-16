from functools import cached_property, total_ordering
from typing import NamedTuple

from hsluv import hex_to_hsluv, hsluv_to_hex, hsluv_to_rgb, rgb_to_hsluv

RGB = tuple[float, float, float]


@total_ordering
class HSLuv(NamedTuple):
    hue: float
    saturation: float
    lightness: float

    def __hash__(self) -> int:
        return hash((self.hue, self.saturation, self.lightness))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HSLuv):
            return hash(self) == hash(other)
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, HSLuv):
            return self.lightness < other.lightness
        return NotImplemented

    @cached_property
    def contrasting_shade(self) -> HSLuv:
        hue, saturation, lightness = self
        return HSLuv(hue, saturation, (lightness + 50) % 100)

    @cached_property
    def contrasting_hue(self) -> HSLuv:
        hue, saturation, lightness = self
        return HSLuv((hue + 180) % 360, saturation, lightness)

    @classmethod
    def from_hex(cls, hex_: str) -> HSLuv:
        return HSLuv(*hex_to_hsluv(hex_))

    @cached_property
    def hex(self) -> RGB:
        return hsluv_to_hex(self)

    @classmethod
    def from_rgb(cls, rgb_: RGB) -> HSLuv:
        return HSLuv(*rgb_to_hsluv(rgb_))

    @cached_property
    def rgb(self) -> RGB:
        return hsluv_to_rgb(self)
