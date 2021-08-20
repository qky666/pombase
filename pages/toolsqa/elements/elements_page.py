from __future__ import annotations

from overrides import overrides
from pombase.types import Number
from pages.toolsqa.web_concept_page import WebConceptPage


class ElementsPage(WebConceptPage):
    default_name = "toolsqa_elements"
    title = "Elements"

    @overrides
    def init_node(self) -> None:
        super().init_node()

    @overrides
    def wait_until_loaded_succeeded(self,
                                    timeout: Number = None,
                                    raise_error: bool = True,
                                    force_count_not_zero: bool = True, ) -> bool:
        if super().wait_until_loaded_succeeded(timeout=timeout,
                                               raise_error=raise_error,
                                               force_count_not_zero=force_count_not_zero) is False:
            return False
        if self.nn_page_title.wait_until_field_value_succeeded(self.title,
                                                               timeout=timeout,
                                                               raise_error=raise_error) is False:
            return False
        return True
