from __future__ import annotations
from overrides import overrides
from pombase.web_node import PageNode, WebNode


class ToolsQAPage(PageNode):
    default_name = "toolsqa"

    @overrides
    def init_node(self) -> None:
        super().init_node()

        # header
        self["header"] = WebNode("header", required=True)
        self["header"]["logo"] = WebNode("a[href='https://demoqa.com']", required=True)
        # TODO: Rebuild it
