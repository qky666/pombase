from __future__ import annotations
import selenium.webdriver.common.by as selenium_by
import selenium.webdriver.common.keys as selenium_keys
# noinspection PyPackageRequirements
import src.testproject.decorator as tp_decorator
import pombase.pom_base_case as pom_base_case


class TestExamples:
    TP_PROJECT_NAME = "pombase"
    TP_JOB_NAME = "TestProject SDK examples"
    TP_TEST_NAME = dict(
        test_simple="Test Simple",
        test_set_timeout="Test Set Timeout",
        test_get_log="Test Get Log",
    )

    @tp_decorator.report_assertion_errors
    def test_simple(self, pb: pom_base_case.PomBaseCase):
        pb.click(".//div[text()='Acepto']", by=selenium_by.By.XPATH)
        pb.type("q", "TestProject" + selenium_keys.Keys.ENTER, by=selenium_by.By.NAME)
        pb.click("a[href='https://testproject.io/']")

    @tp_decorator.report_assertion_errors
    def test_set_timeout(self, pb: pom_base_case.PomBaseCase):
        pb.driver.set_script_timeout(2)
        pb.driver.quit()

    @tp_decorator.report_assertion_errors
    def test_get_log(self, pb: pom_base_case.PomBaseCase):
        pb.driver.get_log("browser")
        pb.driver.quit()
