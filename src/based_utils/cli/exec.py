from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


class FatalError(SystemExit):
    def __init__(self, *args: object) -> None:
        super().__init__(" ".join(str(a) for a in ["💀", *args]))


def killed_by_errors[**P, T](
    f: Callable[P, T] = None,
    /,
    *,
    errors: Iterable[type[Exception]] = None,
    unknown_message: str = None,
) -> Callable[P, T] | Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except tuple(errors or []) as exc:
                raise FatalError(*exc.args) from exc
            except Exception as exc:
                raise FatalError(
                    *([unknown_message] if unknown_message else exc.args)
                ) from exc

        return wrapper

    return decorator if f is None else decorator(f)
