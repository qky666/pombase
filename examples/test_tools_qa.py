from seleniumbase import BaseCase
from examples.pages.tools_qa_main import ToolsQaMain


class ToolsQa(BaseCase):
    def test_start(self):
        self.open("https://demoqa.com/")
        main_page = ToolsQaMain(name="page_tools_qa_main", base_case=self)
        main_page.wait_until_loaded()
