from __future__ import annotations

from typing import Callable
# noinspection PyPackageRequirements
from src.testproject.decorator import report_assertion_errors as tp_report_assertion_errors
from functools import wraps

from . import pombase_config


def report_assertion_errors(func=None, *, screenshot: bool = False):
    if pombase_config.PombaseConfig().tp_dev_token is None:
        def decorator_same_function(fn: Callable) -> Callable:
            @wraps(fn)
            def new_fn(*args, **kwargs):
                return fn(*args, **kwargs)

            return new_fn

        if func:
            return decorator_same_function(func)
        else:
            return decorator_same_function
    else:
        return tp_report_assertion_errors(func, screenshot=screenshot)
