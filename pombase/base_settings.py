from __future__ import annotations

import typing
import math

from seleniumbase.fixtures.base_case import BaseCase


class BaseSettings:
    @staticmethod
    def apply_timeout_multiplier(base_case: BaseCase, timeout: typing.Union[int, float]) -> typing.Union[int, float]:
        timeout_multiplier = base_case.timeout_multiplier
        if timeout_multiplier is not None:
            try:
                timeout_multiplier = float(timeout_multiplier)
                if timeout_multiplier <= 0.5:
                    timeout_multiplier = 0.5
                return int(math.ceil(timeout_multiplier * timeout))
            except ValueError:
                # Wrong data type for timeout_multiplier (expecting int or float)
                return timeout
