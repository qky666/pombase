from __future__ import annotations
from typing import Optional
from _pytest.config import Config as PytestConfig
# noinspection PyPackageRequirements
from src.testproject.enums import SleepTimingType, TakeScreenshotConditionType
# noinspection PyPackageRequirements
from src.testproject.enums.report_type import ReportType

from . import pytest_plugin as pytest_plugin
from . import constant as constants


class PombaseConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PombaseConfig, cls).__new__(cls)
            # Init instance
            cls._instance._pytest_config = None
        return cls._instance

    @property
    def pytest_config(self) -> Optional[PytestConfig]:
        return self._pytest_config

    # noinspection PyAttributeOutsideInit
    @pytest_config.setter
    def pytest_config(self, c: PytestConfig) -> None:
        self._pytest_config = c

    @property
    def pb_disable_testproject(self) -> bool:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.PB_DISABLE_TESTPROJECT
        return v.ini_value(self.pytest_config)

    @property
    def tp_dev_token(self) -> Optional[str]:
        if self.pb_disable_testproject:
            return None
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEV_TOKEN
        return v.ini_value(self.pytest_config)

    @property
    def tp_agent_url(self) -> Optional[str]:
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
    def tp_default_sleep_timing_type(self) -> Optional[SleepTimingType]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEFAULT_SLEEP_TIMING_TYPE
        value = v.ini_value(self.pytest_config)
        return constants.TP_SLEEP_TIMING_TYPE[value] if value is not None else None

    @property
    def tp_default_take_screenshot_condition_type(self) -> TakeScreenshotConditionType:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DEFAULT_TAKE_SCREENSHOT_CONDITION_TYPE
        value = v.ini_value(self.pytest_config)
        return constants.TP_TAKE_SCREENSHOT_CONDITION_TYPE[value]

    @property
    def tp_project_name(self) -> Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_PROJECT_NAME
        return v.ini_value(self.pytest_config)

    @property
    def tp_job_name(self) -> Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_JOB_NAME
        return v.ini_value(self.pytest_config)

    @property
    def tp_disable_auto_reporting(self) -> bool:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_DISABLE_AUTO_REPORTING
        return v.ini_value(self.pytest_config)

    @property
    def tp_report_type(self) -> ReportType:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_REPORT_TYPE
        value = v.ini_value(self.pytest_config)
        return constants.TP_REPORT_TYPE[value]

    @property
    def tp_report_name(self) -> Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_REPORT_NAME
        return v.ini_value(self.pytest_config)

    @property
    def tp_report_path(self) -> Optional[str]:
        v: pytest_plugin.PytestVar = pytest_plugin.PytestVar.TP_REPORT_PATH
        return v.ini_value(self.pytest_config)
