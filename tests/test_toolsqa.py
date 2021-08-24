from __future__ import annotations

from pombase import PombaseCase, report_assertion_errors
from pages.toolsqa.home.home_page import HomePage
from pages.toolsqa.elements.elements_page import ElementsPage
from pages.toolsqa.elements.web_tables_page import WebTablesPage
from pages.toolsqa.elements.web_tables_registration_form_page import WebTablesRegistrationFormPage


class TestToolsQA:
    TP_PROJECT_NAME = "pombase"
    TP_JOB_NAME = "ToolsQA examples"
    TP_TEST_NAME = dict(test_web_tables="Test Web Tables")

    @report_assertion_errors
    def test_web_tables(self, pb: PombaseCase):
        page = HomePage(pb)
        page.wait_until_loaded_succeeded()
        page.swn_cards__swn_elements.click()

        page = ElementsPage(pb)
        page.wait_until_loaded_succeeded()
        page.swn_left_pannel__swn_elements.do_select_sub_element("Web Tables")

        page = WebTablesPage(pb)
        page.wait_until_loaded_succeeded()
        page.swn_table_wrapper__swn_add.click()

        page = WebTablesRegistrationFormPage(pb)
        page.wait_until_loaded_succeeded()
