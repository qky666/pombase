from __future__ import annotations
import typing
import _pytest.config as pt_config
# noinspection PyPackageRequirements
import src.testproject.enums as tp_enums
# noinspection PyPackageRequirements
import src.testproject.enums.report_type as report_type

import pombase.pytest_plugin as pytest_plugin
import pombase.constant as constants


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # Init instance
            cls._instance._pytest_config = None
        return cls._instance

    @property
    def pytest_config(self) -> typing.Optional[pt_config.Config]:
        return self._pytest_config

    @pytest_config.setter
    def pytest_config(self, c: pt_config.Config) -> None:
        self._pytest_config = c

    @property
    def tp_dev_token(self) -> typing.Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEV_TOKEN
        return v.ini_value(self.pytest_config)

    @property
    def tp_agent_url(self) -> typing.Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_AGENT_URL
        return v.ini_value(self.pytest_config)

    @property
    def tp_default_timeout(self) -> int:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEFAULT_TIMEOUT
        value = v.ini_value(self.pytest_config)
        return int(value)

    @property
    def tp_default_sleep_time(self) -> int:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEFAULT_SLEEP_TIME
        value = v.ini_value(self.pytest_config)
        return int(value)

    @property
    def tp_default_sleep_timing_type(self) -> typing.Optional[tp_enums.SleepTimingType]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEFAULT_SLEEP_TIMING_TYPE
        value = v.ini_value(self.pytest_config)
        return constants.TP_SLEEP_TIMING_TYPE[value] if value is not None else None

    @property
    def tp_default_take_screenshot_condition_type(self) -> tp_enums.TakeScreenshotConditionType:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEFAULT_TAKE_SCREENSHOT_CONDITION_TYPE
        value = v.ini_value(self.pytest_config)
        return constants.TP_TAKE_SCREENSHOT_CONDITION_TYPE[value]

    @property
    def tp_project_name(self) -> typing.Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_PROJECT_NAME
        return v.ini_value(self.pytest_config)

    @property
    def tp_job_name(self) -> typing.Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_JOB_NAME
        return v.ini_value(self.pytest_config)

    @property
    def tp_disable_auto_reporting(self) -> bool:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DISABLE_AUTO_REPORTING
        return v.ini_value(self.pytest_config)

    @property
    def tp_report_type(self) -> report_type.ReportType:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_REPORT_TYPE
        value = v.ini_value(self.pytest_config)
        return constants.TP_REPORT_TYPE[value]

    @property
    def tp_report_name(self) -> typing.Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_REPORT_NAME
        return v.ini_value(self.pytest_config)

    @property
    def tp_report_path(self) -> typing.Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_REPORT_PATH
        return v.ini_value(self.pytest_config)
