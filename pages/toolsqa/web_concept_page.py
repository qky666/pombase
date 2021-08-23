from __future__ import annotations

from overrides import overrides
from pombase import SingleWebNode, PageNode, NumberType


class AccordionElementNode(SingleWebNode):
    @overrides
    def __init__(self, title: str):
        self.title = title
        super().__init__(
            f".//div[contains(@class,'element-group')][.//div[contains(@class,'header-text') and .='{title}']]",
            required=True,
        )

    @overrides
    def init_node(self) -> None:
        super().init_node()

        self.swn_title = SingleWebNode("div.header-text", required=True)

        self.swn_element_list = SingleWebNode("div.element-list.show")

    @property
    def is_expanded(self) -> bool:
        return self.swn_element_list.is_element_visible()

    @is_expanded.setter
    def is_expanded(self, value: bool) -> None:
        if self.is_expanded != value:
            self.swn_title.click()

    def select_sub_element(self, name: str) -> None:
        element_list = self.swn_element_list

        class SubElement(SingleWebNode):
            @overrides
            def __init__(self, title: str) -> None:
                super().__init__(
                    f".//ul[contains(@class,'menu-list')]/li[contains(@class,'btn')][.='{title}']",
                    parent=element_list,
                )
                self.title = title

        self.is_expanded = True

        sub_element = SubElement(name)
        sub_element.click()
        sub_element.parent = None


class WebConceptPage(PageNode):
    # TODO: Remove this
    # default_name = "pn_toolsqa_web_concept"
    title = ""

    @overrides
    def init_node(self) -> None:
        super().init_node()

        self.swn_page_title = SingleWebNode(".//div[contains(@class,'main-header')]", required=True)

        # left pannel
        self.swn_left_pannel = SingleWebNode("div.left-pannel", required=True)
        self.swn_left_pannel__swn_elements = AccordionElementNode("Elements")
        self.swn_left_pannel__swn_forms = AccordionElementNode("Forms")
        self.swn_left_pannel__swn_alerts_frame_windows = AccordionElementNode("Alerts, Frame & Windows")
        self.swn_left_pannel__swn_widgets = AccordionElementNode("Widgets")
        self.swn_left_pannel__swn_interactions = AccordionElementNode("Interactions")
        self.swn_left_pannel__swn_book_store_application = AccordionElementNode("Book Store Application")

    @overrides
    def override_wait_until_loaded(self, timeout: NumberType = None) -> None:
        super().override_wait_until_loaded(timeout)

        # Page title is self.title
        self.swn_page_title.wait_until_field_value_succeeded(lambda value: value == self.title, timeout=timeout)
