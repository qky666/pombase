from __future__ import annotations
from selenium.common.exceptions import InvalidArgumentException, WebDriverException
# noinspection PyPackageRequirements
from src.testproject.sdk.drivers import webdriver as tp_webdriver
# noinspection PyPackageRequirements
from src.testproject.classes import StepSettings, DriverStepSettings
# noinspection PyPackageRequirements
from src.testproject.enums import TakeScreenshotConditionType

from . import types as tp_types


class Chrome(tp_webdriver.Chrome):
    def set_script_timeout(self, time_to_wait: tp_types.NumberType) -> None:
        step_settings = StepSettings(
            timeout=int(time_to_wait),
            always_pass=True,
            screenshot_condition=TakeScreenshotConditionType.Never,
        )
        with DriverStepSettings(self, step_settings):
            try:
                super().set_script_timeout(time_to_wait)
            except InvalidArgumentException:
                pass


class Firefox(tp_webdriver.Firefox):
    def get_log(self, log_type: str):
        step_settings = StepSettings(
            always_pass=True,
            screenshot_condition=TakeScreenshotConditionType.Never,
        )
        with DriverStepSettings(self, step_settings):
            try:
                return super().get_log(log_type)
            except WebDriverException:
                pass


class Edge(tp_webdriver.Edge):
    pass


class Ie(tp_webdriver.Ie):
    pass


class Safari(tp_webdriver.Safari):
    pass


class Remote(tp_webdriver.Remote):
    pass


class Generic(tp_webdriver.Generic):
    pass
