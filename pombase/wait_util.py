from __future__ import annotations

import typing
import time


def wait_until(f: typing.Callable,
               args: list = None,
               kwargs: dict = None,
               timeout: typing.Union[int, float] = 10,
               step: typing.Union[int, float] = 0.5,
               expected: typing.Any = True,
               equals: bool = True,
               raise_error: str = None, ) -> (bool, typing.Any):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    assert timeout >= 0, f"timeout should be >= 0. timeout = {timeout}"
    assert step > 0, f"step should be > 0. step = {step}"

    current = time.time()
    start = current
    stop = start + timeout
    value = f(*args, **kwargs)
    while current <= stop:
        if (value == expected) is equals:
            return True, value
        after = time.time()
        if after < current + step:
            time.sleep(current + step - after)
        current = time.time()
        value = f(*args, **kwargs)
    else:
        if raise_error is not None:
            raise TimeoutError(
                f"{raise_error}. f='{f}', args='{args}', kwargs='{kwargs}', timeout='{timeout}', step='{step}', "
                f"expected='{expected}', equals='{equals}'",
            )
        else:
            return False, value
