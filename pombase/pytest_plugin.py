from __future__ import annotations
import typing
import pytest
import _pytest.config as pt_config
import _pytest.fixtures as pt_fixtures
import os
import enum
import seleniumbase.config as sb_config
# noinspection PyPackageRequirements
import src.testproject.enums as tp_enums
# noinspection PyPackageRequirements
import src.testproject.enums.environmentvariable as environmentvariable

import pombase.constant as constants
import pombase.config as pb_config
import pombase.pom_base_case as pom_base_case
import pombase.util as util

PytestVariableType = typing.Literal['string', 'pathlist', 'args', 'linelist', 'bool']


@enum.unique
class PytestVar(enum.Enum):
    """Enumeration of environment variable names used"""

    TP_DEV_TOKEN: PytestVar = ("TP_DEV_TOKEN", "TestProject developer token", "string", None)
    TP_AGENT_URL: PytestVar = ("TP_AGENT_URL", "TestProject agent url", "string", None)
    TP_DEFAULT_TIMEOUT: PytestVar = (
        "TP_DEFAULT_TIMEOUT",
        "TestProject default step timeout (milliseconds)",
        "string",
        "-1",
    )
    TP_DEFAULT_SLEEP_TIME: PytestVar = (
        "TP_DEFAULT_SLEEP_TIME",
        "TestProject default sleep time (milliseconds)",
        "string",
        "0",
    )
    TP_DEFAULT_SLEEP_TIMING_TYPE: PytestVar = (
        "TP_DEFAULT_SLEEP_TIMING_TYPE",
        f"TestProject default sleep timing type {tuple(constants.TP_SLEEP_TIMING_TYPE.keys())}",
        "string",
        None,
    )
    TP_DEFAULT_TAKE_SCREENSHOT_CONDITION_TYPE: PytestVar = (
        "TP_DEFAULT_TAKE_SCREENSHOT_CONDITION_TYPE",
        f"TestProject default take screenshot condition type "
        f"{tuple(constants.TP_TAKE_SCREENSHOT_CONDITION_TYPE.keys())}",
        "string",
        "failure",
    )
    TP_PROJECT_NAME: PytestVar = (
        tp_enums.EnvironmentVariable.TP_PROJECT_NAME.value,
        "TestProject project name",
        "string",
        None,
    )
    TP_JOB_NAME: PytestVar = (
        tp_enums.EnvironmentVariable.TP_JOB_NAME.value,
        "TestProject job name",
        "string",
        None,
    )
    TP_DISABLE_AUTO_REPORTING: PytestVar = (
        tp_enums.EnvironmentVariable.TP_DISABLE_AUTO_REPORTING.value,
        "Disable all reports in TestProject",
        "bool",
        False,
    )
    TP_REPORT_TYPE: PytestVar = (
        "TP_REPORT_TYPE",
        f"TestProject report type {tuple(constants.TP_REPORT_TYPE.keys())}",
        "string",
        "cloud_and_local",
    )
    TP_REPORT_NAME: PytestVar = (
        "TP_REPORT_NAME",
        f"TestProject report name",
        "string",
        None,
    )
    TP_REPORT_PATH: PytestVar = (
        "TP_REPORT_PATH",
        f"TestProject report path",
        "string",
        None,
    )

    def __init__(self, var_name: str,
                 help_text: str,
                 var_type: PytestVariableType,
                 default_value: typing.Optional[str]):
        self.var_name = var_name
        self.help_text = help_text
        self.var_type = var_type
        self.default_value = default_value

    @property
    def env_var_name(self) -> str:
        return self.var_name.upper()

    @property
    def ini_name(self) -> str:
        return self.var_name.lower()

    def remove_env_var(self) -> None:
        """Try and remove the environment variable, proceed if the variable doesn't exist"""
        try:
            os.environ.pop(self.env_var_name)
        except KeyError:
            pass

    def env_value(self) -> typing.Optional[str]:
        v = os.environ.get(self.env_var_name, None)
        return v if v not in constants.ALMOST_NONE else None

    def ini_value(self, config: pt_config.Config) -> typing.Union[str, list, list[str], bool]:
        v = config.getini(self.ini_name)
        return v if v not in constants.ALMOST_NONE else None

    def addini(self, parser: pt_config.argparsing.Parser) -> None:
        kwargs = {}
        env_var_value = self.env_value()
        default = env_var_value if env_var_value is not None else self.default_value
        if default is not None:
            if self.var_type == "bool":
                if isinstance(default, bool) is False:
                    if isinstance(default, int):
                        default = False if default == 0 else True
                    elif isinstance(default, str):
                        default = True if default.lower() in ["true", "1"] else False
            else:
                assert self.var_type == "string", f"var_type not supported: {self.var_type}"
            kwargs["default"] = default
        parser.addini(self.ini_name, help=self.help_text, type=self.var_type, **kwargs)


def pytest_addoption(parser: pt_config.argparsing.Parser) -> None:
    for pytest_var in PytestVar:
        pytest_var: PytestVar
        pytest_var.addini(parser)


def pytest_configure(config: pt_config.Config) -> None:
    pb_config.Config().pytest_config = config


@pytest.fixture()
def pb(request: pt_fixtures.FixtureRequest):
    """PomBase as a pytest fixture.
    Usage example: "def test_one(pb):"
    You may need to use this for tests that use other pytest fixtures."""

    class BaseClass(pom_base_case.PomBaseCase):
        def setUp(self, masterqa_mode=False):
            super().setUp(masterqa_mode)

        def tearDown(self):
            self.save_teardown_screenshot()
            super().tearDown()

        def base_method(self):
            pass

    # Pombase
    tp_project_name_var: PytestVar = PytestVar.TP_PROJECT_NAME
    tp_job_name_var: PytestVar = PytestVar.TP_JOB_NAME
    tp_test_name_env_var_name: str = environmentvariable.EnvironmentVariable.TP_TEST_NAME.value

    if request.cls:
        # SeleniumBase
        request.cls.sb = BaseClass("base_method")

        # PomBase
        request.cls.sb.tp_project_name = util.first_not_none(
            getattr(request.cls, tp_project_name_var.ini_name, None),
            getattr(request.cls, tp_project_name_var.env_var_name, None),
            getattr(request.module, tp_project_name_var.ini_name, None),
            getattr(request.module, tp_project_name_var.env_var_name, None),
        )
        request.cls.sb.tp_job_name = util.first_not_none(
            getattr(request.cls, tp_job_name_var.ini_name, None),
            getattr(request.cls, tp_job_name_var.env_var_name, None),
            getattr(request.module, tp_job_name_var.ini_name, None),
            getattr(request.module, tp_job_name_var.env_var_name, None),
        )
        test_name_dict = util.first_not_none(
            getattr(request.cls, tp_test_name_env_var_name, None),
            getattr(request.cls, tp_test_name_env_var_name.lower(), None),
            getattr(request.module, tp_test_name_env_var_name, None),
            getattr(request.module, tp_test_name_env_var_name.lower(), None),
        )
        test_name = None
        if isinstance(test_name_dict, dict):
            test_name = test_name_dict.get(request.node.name, None)
        if test_name is not None:
            request.cls.sb.tp_test_name = test_name

        # SeleniumBase
        request.cls.sb.setUp()
        request.cls.sb._needs_tearDown = True
        request.cls.sb._using_sb_fixture = True
        request.cls.sb._using_sb_fixture_class = True
        sb_config._sb_node[request.node.nodeid] = request.cls.sb
        yield request.cls.sb
        if request.cls.sb._needs_tearDown:
            request.cls.sb.tearDown()
            request.cls.sb._needs_tearDown = False
    else:
        # SeleniumBase
        sb = BaseClass("base_method")

        # PomBase
        sb.tp_project_name = util.first_not_none(
            getattr(request.module, tp_project_name_var.ini_name, None),
            getattr(request.module, tp_project_name_var.env_var_name, None),
        )
        sb.tp_job_name = util.first_not_none(
            getattr(request.module, tp_job_name_var.ini_name, None),
            getattr(request.module, tp_job_name_var.env_var_name, None),
        )
        test_name_dict = util.first_not_none(
            getattr(request.module, tp_test_name_env_var_name, None),
            getattr(request.module, tp_test_name_env_var_name.lower(), None),
        )
        test_name = None
        if isinstance(test_name_dict, dict):
            test_name = test_name_dict.get(request.node.name, None)
        if test_name is not None:
            request.cls.sb.tp_test_name = test_name

        # SeleniumBase
        sb.setUp()
        sb._needs_tearDown = True
        sb._using_sb_fixture = True
        sb._using_sb_fixture_no_class = True
        sb_config._sb_node[request.node.nodeid] = sb
        yield sb
        if sb._needs_tearDown:
            sb.tearDown()
            sb._needs_tearDown = False
