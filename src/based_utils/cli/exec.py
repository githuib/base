from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class FatalError(SystemExit):
    def __init__(self, *args: object) -> None:
        super().__init__(" ".join(str(a) for a in ["💀", *args]))


def killed_by_errors[**P, T](
    *errors: type[Exception], unknown_message: str = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except tuple(errors or []) as exc:
                raise FatalError(*exc.args) from exc
            except Exception as exc:
                if unknown_message:
                    raise FatalError(unknown_message) from exc
                raise FatalError(*exc.args) from exc

        return wrapper

    return decorator


def killed_by[E: Exception, **P, T](
    *errors: type[E],
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except errors as exc:
                raise FatalError(*exc.args) from exc

        return wrapper

    return decorator


def catch_unknown_errors[**P, T](
    unknown_message: str = "Unknown error",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                raise FatalError(unknown_message) from exc

        return wrapper

    return decorator
