from pombase.pom_base_case import PomBaseCase
from examples.pages.tools_qa_main import ToolsQaMain


class ToolsQa(PomBaseCase):
    def test_start(self):
        self.open("https://demoqa.com/")
        main_page = ToolsQaMain.load_node_from_file(self)
        main_page.wait_until_loaded()
