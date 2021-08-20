from __future__ import annotations
from typing import Type, Union, MutableMapping
# noinspection PyPackageRequirements
from src.testproject.enums import SleepTimingType, TakeScreenshotConditionType
# noinspection PyPackageRequirements
from src.testproject.enums.report_type import ReportType

import pombase.util as pb_util
import pombase.webdriver as pb_webdriver

PbWebDriver = Type[Union[pb_webdriver.Chrome,
                         pb_webdriver.Edge,
                         pb_webdriver.Firefox,
                         pb_webdriver.Ie,
                         pb_webdriver.Remote,
                         pb_webdriver.Safari,
                         pb_webdriver.Generic, ]]

TP_DRIVER_CLASS: MutableMapping[str, PbWebDriver] = \
    pb_util.CaseInsensitiveDict(
        chrome=pb_webdriver.Chrome,
        edge=pb_webdriver.Edge,
        firefox=pb_webdriver.Firefox,
        ie=pb_webdriver.Ie,
        remote=pb_webdriver.Remote,
        safari=pb_webdriver.Safari,
        generic=pb_webdriver.Generic,
    )

TP_SLEEP_TIMING_TYPE: MutableMapping[str, SleepTimingType] = pb_util.CaseInsensitiveDict(
    before=SleepTimingType.Before,
    after=SleepTimingType.After,
    inherit=SleepTimingType.Inherit,
)

TP_TAKE_SCREENSHOT_CONDITION_TYPE: MutableMapping[str, TakeScreenshotConditionType] = \
    pb_util.CaseInsensitiveDict(
        never=TakeScreenshotConditionType.Never,
        success=TakeScreenshotConditionType.Success,
        failure=TakeScreenshotConditionType.Failure,
        always=TakeScreenshotConditionType.Always,
        suspend=TakeScreenshotConditionType.Suspend,
        inherit=TakeScreenshotConditionType.Inherit,
    )

TP_REPORT_TYPE: MutableMapping[str, ReportType] = pb_util.CaseInsensitiveDict(
    cloud=ReportType.CLOUD,
    local=ReportType.LOCAL,
    cloud_and_local=ReportType.CLOUD_AND_LOCAL,
)

ALMOST_NONE = [None, "", [], (), {}]
