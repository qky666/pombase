from __future__ import annotations
import typing
# noinspection PyPackageRequirements
import src.testproject.enums as tp_enums
# noinspection PyPackageRequirements
import src.testproject.enums.report_type as report_type

import pombase.util as util
import pombase.webdriver as tp_webdriver


TP_DRIVER_CLASS: typing.MutableMapping[str, typing.Type[typing.Union[tp_webdriver.Chrome,
                                                                     tp_webdriver.Edge,
                                                                     tp_webdriver.Firefox,
                                                                     tp_webdriver.Ie,
                                                                     tp_webdriver.Remote,
                                                                     tp_webdriver.Safari,
                                                                     tp_webdriver.Generic, ]]] = \
    util.CaseInsensitiveDict(
        chrome=tp_webdriver.Chrome,
        edge=tp_webdriver.Edge,
        firefox=tp_webdriver.Firefox,
        ie=tp_webdriver.Ie,
        remote=tp_webdriver.Remote,
        safari=tp_webdriver.Safari,
        generic=tp_webdriver.Generic,
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
