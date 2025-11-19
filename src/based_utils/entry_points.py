from based_utils import log
from based_utils.cli import LogLevel
from based_utils.cli.coloring import color_lines


def print_colors() -> None:
    with log.context(LogLevel.INFO):
        for line in color_lines():
            log.get_logger().info(line)
