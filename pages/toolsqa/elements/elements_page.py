from __future__ import annotations

from overrides import overrides
from pages.toolsqa.web_concept_page import WebConceptPage


class ElementsPage(WebConceptPage):
    # TODO: Remove this
    # default_name = "pn_toolsqa_elements"
    title = "Elements"

    @overrides
    def init_node(self) -> None:
        super().init_node()
