from __future__ import annotations
import typing
import selenium.common.exceptions as selenium_exceptions
# noinspection PyPackageRequirements
import src.testproject.sdk.drivers.webdriver as tp_webdriver
# noinspection PyPackageRequirements
import src.testproject.classes as tp_classes
# noinspection PyPackageRequirements
import src.testproject.enums as tp_enums


# Type alias
Number = typing.Union[int, float]


class Chrome(tp_webdriver.Chrome):
    def set_script_timeout(self, time_to_wait: Number) -> None:
        step_settings = tp_classes.StepSettings(
            timeout=int(time_to_wait),
            always_pass=True,
            screenshot_condition=tp_enums.TakeScreenshotConditionType.Never,
        )
        with tp_classes.DriverStepSettings(self, step_settings):
            try:
                super().set_script_timeout(time_to_wait)
            except selenium_exceptions.InvalidArgumentException:
                pass


class Firefox(tp_webdriver.Firefox):
    def get_log(self, log_type: str):
        step_settings = tp_classes.StepSettings(
            always_pass=True,
            screenshot_condition=tp_enums.TakeScreenshotConditionType.Never,
        )
        with tp_classes.DriverStepSettings(self, step_settings):
            try:
                return super().get_log(log_type)
            except selenium_exceptions.WebDriverException:
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
