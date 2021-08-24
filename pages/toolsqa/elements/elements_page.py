from __future__ import annotations

from overrides import overrides
from pages.toolsqa.web_concept_page import WebConceptPage


class ElementsPage(WebConceptPage):
    title = "Elements"

    @overrides
    def init_node(self) -> None:
        super().init_node()
