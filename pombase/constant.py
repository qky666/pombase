from __future__ import annotations
import typing
# noinspection PyPackageRequirements
import src.testproject.enums as tp_enums
# noinspection PyPackageRequirements
import src.testproject.enums.report_type as report_type

import pombase.util as util
import pombase.webdriver as pb_webdriver

PbWebDriver = typing.Type[typing.Union[pb_webdriver.Chrome,
                                       pb_webdriver.Edge,
                                       pb_webdriver.Firefox,
                                       pb_webdriver.Ie,
                                       pb_webdriver.Remote,
                                       pb_webdriver.Safari,
                                       pb_webdriver.Generic, ]]


TP_DRIVER_CLASS: typing.MutableMapping[str, PbWebDriver] = \
    util.CaseInsensitiveDict(
        chrome=pb_webdriver.Chrome,
        edge=pb_webdriver.Edge,
        firefox=pb_webdriver.Firefox,
        ie=pb_webdriver.Ie,
        remote=pb_webdriver.Remote,
        safari=pb_webdriver.Safari,
        generic=pb_webdriver.Generic,
    )

TP_SLEEP_TIMING_TYPE: typing.MutableMapping[str, tp_enums.SleepTimingType] = util.CaseInsensitiveDict(
    before=tp_enums.SleepTimingType.Before,
    after=tp_enums.SleepTimingType.After,
    inherit=tp_enums.SleepTimingType.Inherit,
)

TP_TAKE_SCREENSHOT_CONDITION_TYPE: typing.MutableMapping[str, tp_enums.TakeScreenshotConditionType] = \
    util.CaseInsensitiveDict(
        never=tp_enums.TakeScreenshotConditionType.Never,
        success=tp_enums.TakeScreenshotConditionType.Success,
        failure=tp_enums.TakeScreenshotConditionType.Failure,
        always=tp_enums.TakeScreenshotConditionType.Always,
        suspend=tp_enums.TakeScreenshotConditionType.Suspend,
        inherit=tp_enums.TakeScreenshotConditionType.Inherit,
    )

TP_REPORT_TYPE: typing.MutableMapping[str, report_type.ReportType] = util.CaseInsensitiveDict(
    cloud=report_type.ReportType.CLOUD,
    local=report_type.ReportType.LOCAL,
    cloud_and_local=report_type.ReportType.CLOUD_AND_LOCAL,
)

ALMOST_NONE = [None, "", [], (), {}]
