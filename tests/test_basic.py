from __future__ import annotations
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# noinspection PyPackageRequirements
from src.testproject.decorator import report_assertion_errors
import pombase.pombase_case as pom_base_case


class TestBasic:
    TP_PROJECT_NAME = "pombase"
    TP_JOB_NAME = "TestProject SDK examples"
    TP_TEST_NAME = dict(
        test_simple="Test Simple",
        test_set_timeout="Test Set Timeout",
        test_get_log="Test Get Log",
    )

    @report_assertion_errors
    def test_simple(self, pb: pom_base_case.PombaseCase):
        pb.click(".//div[text()='Acepto']", by=By.XPATH)
        pb.type("q", "TestProject" + Keys.ENTER, by=By.NAME)
        pb.click("a[href='https://testproject.io/']")

    @report_assertion_errors
    def test_set_timeout(self, pb: pom_base_case.PombaseCase):
        pb.driver.set_script_timeout(2)
        pb.driver.quit()

    @report_assertion_errors
    def test_get_log(self, pb: pom_base_case.PombaseCase):
        pb.driver.get_log("browser")
        pb.driver.quit()
