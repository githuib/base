from dataclasses import dataclass
from functools import cached_property
from typing import overload

from hsluv import hex_to_hsluv, hsluv_to_hex, hsluv_to_rgb, rgb_to_hsluv


@dataclass(frozen=True)
class RGB:
    red: int
    green: int
    blue: int


@dataclass(frozen=True, order=True)
class HSLuv:
    lightness: float
    saturation: float
    hue: float

    @cached_property
    def contrasting_shade(self) -> HSLuv:
        """
        Color with a lightness that contrasts with the current color.

        Color with a 50% lower or higher lightness than the current color,
        while maintaining the same hue and saturation (so it can for example
        be used as background color).

        :return: HSLuv representation of the contrasting shade

        >>> HSLuv.from_hex("08f").contrasting_shade.hex
        '001531'
        >>> HSLuv.from_hex("0f8").contrasting_shade.hex
        '006935'
        >>> HSLuv.from_hex("80f").contrasting_shade.hex
        'ebe4ff'
        >>> HSLuv.from_hex("8f0").contrasting_shade.hex
        '366b00'
        >>> HSLuv.from_hex("f08").contrasting_shade.hex
        '2b0012'
        >>> HSLuv.from_hex("f80").contrasting_shade.hex
        '4a2300'
        """
        return HSLuv((self.lightness + 50) % 100, self.saturation, self.hue)

    @cached_property
    def contrasting_hue(self) -> HSLuv:
        """
        Color with a hue that contrasts with the current color.

        Color with a 180° different hue than the current color,
        while maintaining the same saturation and perceived lightness.

        :return: HSLuv representation of the contrasting hue

        >>> HSLuv.from_hex("08f").contrasting_hue.hex
        '9c8900'
        >>> HSLuv.from_hex("0f8").contrasting_hue.hex
        'ffd1f5'
        >>> HSLuv.from_hex("80f").contrasting_hue.hex
        '5c6900'
        >>> HSLuv.from_hex("8f0").contrasting_hue.hex
        'f6d9ff'
        >>> HSLuv.from_hex("f08").contrasting_hue.hex
        '009583'
        >>> HSLuv.from_hex("f80").contrasting_hue.hex
        '00b8d1'
        """
        return HSLuv(self.lightness, self.saturation, (self.hue + 180) % 360)

    @overload
    @classmethod
    def from_hex(cls, rgb_hex: str) -> HSLuv: ...

    @overload
    @classmethod
    def from_hex(cls, rgb_hex: None) -> None: ...

    @classmethod
    def from_hex(cls, rgb_hex: str | None) -> HSLuv | None:
        """
        Create a HSLuv from an RGB hex string.

        :param rgb_hex: RGB hex string (may start with '#') or None
        :return: HSLuv instance

        >>> HSLuv.from_hex(None) is None
        True
        >>> HSLuv.from_hex("3").hex
        '333333'
        >>> HSLuv.from_hex("03").hex
        '030303'
        >>> HSLuv.from_hex("303").hex
        '330033'
        >>> HSLuv.from_hex("808303").hex
        '808303'
        """
        if rgb_hex is None:
            return None

        rgb_hex = rgb_hex.removeprefix("#").lower()

        if len(rgb_hex) == 1:
            # 3 -> r=33, g=33, b=33
            r = g = b = rgb_hex * 2

        elif len(rgb_hex) == 2:
            # 03 -> r=03, g=03, b=03
            r = g = b = rgb_hex

        elif len(rgb_hex) == 3:
            # 303 -> r=33, g=00, b=33
            r1, g1, b1 = iter(rgb_hex)
            r, g, b = r1 * 2, g1 * 2, b1 * 2

        elif len(rgb_hex) == 6:
            # 808303 -> r=80, g=83, b=03
            r1, r2, g1, g2, b1, b2 = iter(rgb_hex)
            r, g, b = r1 + r2, g1 + g2, b1 + b2

        else:
            raise ValueError(rgb_hex)

        h, s, li = hex_to_hsluv(f"#{r}{g}{b}")
        return HSLuv(li, s, h)

    @cached_property
    def hex(self) -> str:
        return hsluv_to_hex((self.hue, self.saturation, self.lightness))[1:]

    @overload
    @classmethod
    def from_rgb(cls, rgb: RGB) -> HSLuv: ...

    @overload
    @classmethod
    def from_rgb(cls, rgb: None) -> None: ...

    @classmethod
    def from_rgb(cls, rgb: RGB | None) -> HSLuv | None:
        """
        Create a HSLuv from RGB values.

        :param rgb: RGB instance or None
        :return: HSLuv instance

        >>> HSLuv.from_rgb(None) is None
        True
        >>> HSLuv.from_rgb(RGB(128, 131, 3)).rgb
        RGB(red=127, green=131, blue=3)
        """
        if rgb is None:
            return None
        h, s, li = rgb_to_hsluv((rgb.red / 255, rgb.green / 255, rgb.blue / 255))
        return HSLuv(li, s, h)

    @cached_property
    def rgb(self) -> RGB:
        r, g, b = hsluv_to_rgb((self.hue, self.saturation, self.lightness))
        return RGB(int(r * 255), int(g * 255), int(b * 255))
