import sys
import time
from collections.abc import Iterable
from itertools import count
from os import get_terminal_size
from typing import TYPE_CHECKING, cast

from based_utils.calx import randf
from based_utils.colors import Color
from based_utils.data.iterators import do_and_count

from .formats import LINE_CLEAR, LINE_UP, Colored

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

type Lines = Iterable[str]


def refresh_lines(lines: Lines) -> int:
    def action(line: str) -> None:
        sys.stdout.write(line + "\n")

    return do_and_count(lines, action)


def clear_lines(amount: int) -> None:
    for _ in range(amount):
        sys.stdout.write(LINE_UP + LINE_CLEAR)


def animate[T](
    items: Iterable[T],
    format_item: Callable[[T], Lines] | None = None,
    *,
    fps: int = 60,
    keep_last: bool = True,
    only_every_nth: int = 1,
) -> Iterator[T]:
    def fmt(item_: T) -> Lines:
        return cast("Lines", item_) if format_item is None else format_item(item_)

    lines_written = 0
    for i, item in enumerate(items):
        yield item
        if i % only_every_nth != 0:
            continue

        clear_lines(lines_written)
        lines_written = refresh_lines(fmt(item))
        time.sleep(1 / fps)

    if not keep_last:
        clear_lines(lines_written)


def animated(
    lines: Lines,
    *frame_n: Callable[[Lines, int], Lines],
    num_frames: int = None,
    min_width: int = None,
    fill_char: str = " ",
) -> Callable[[], Iterator[Lines]]:
    def func() -> Iterator[Lines]:
        max_width, _max_height = get_terminal_size()
        block = list(lines)
        block_width = max(len(line) for line in block)
        width_ = max_width if min_width is None else min(min_width, max_width)
        frame_0: Lines = [
            line.ljust(block_width, fill_char).center(width_, fill_char)
            for line in block
        ]
        for i in count():
            n = i % (num_frames or width_)
            frame = frame_0
            for f in frame_n:
                frame = f(frame, n)
            yield frame

    return func


def moving_forward(frame_0: Lines, n: int) -> Lines:
    return [(line[-n:] + line[:-n]) for line in frame_0]


def fuck_me_sideways(frame_0: Lines, n: int) -> Lines:
    lines = list(frame_0)
    h = len(lines) - 1
    hh = h // 2
    return [
        (
            line[(n * -i) if i < hh else n * (h - i) :]
            + line[: (n * -i) if i < hh else n * (h - i)]
        )
        for i, line in enumerate(lines)
    ]


def changing_colors(frame_0: Lines, n: int, *, amount_of_hues: int = 101) -> Lines:
    color = Color.from_fields(hue=n / amount_of_hues, lightness=0.75)
    background = color.contrasting_hue.contrasting_shade
    return [Colored(line, color, background).formatted for line in frame_0]


def flashing(
    frame_0: Lines,
    n: int,
    intensity: float = 0.1,
    hue: float = None,
    amount_of_hues: int = 101,
) -> Lines:
    flash = n % 5 == 0 and randf() < intensity * 5
    h = randf() if flash else n / amount_of_hues if hue is None else hue
    fg = Color.from_fields(hue=h, lightness=0.5)
    bg = fg.shade(0.2)
    return [
        Colored(
            line,
            fg.but_with(lightness=0.3) if flash else fg,
            bg.but_with(lightness=0.9) if flash else bg,
        ).formatted
        for line in frame_0
    ]
