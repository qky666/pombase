from __future__ import annotations
from overrides import overrides
from pombase import PageNode, SingleWebNode


class ToolsQAPage(PageNode):
    # TODO: Remove this
    # default_name = "pn_toolsqa"

    @overrides
    def init_node(self) -> None:
        super().init_node()

        self.swn_header = SingleWebNode("header", required=True)
        self.swn_header__swn_logo = SingleWebNode("a[href='https://demoqa.com']", required=True)
