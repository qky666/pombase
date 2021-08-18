from __future__ import annotations

from overrides import overrides
from pombase.web_node import WebNode, Locator


class ToolsQAPage(WebNode):
    default_name = "toolsqa"

    @overrides
    def init_node(self) -> None:
        super().init_node()

        # header
        header = WebNode(Locator("header"), parent=self, name="header", valid_count=1)
        WebNode(Locator("a[href='https://demoqa.com']"), parent=header, name="logo", valid_count=1)

    @overrides
    def init_named_nodes(self) -> None:
        self.nn_header = self.find_node("header")
        self.nn_header__logo = self.find_node("header__logo")
