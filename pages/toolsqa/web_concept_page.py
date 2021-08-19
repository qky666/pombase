from __future__ import annotations

from overrides import overrides
from pombase.web_node import GenericNode, Locator
from inflection import parameterize


class AccordionElement(GenericNode):
    @overrides
    def __init__(self, title: str, parent: GenericNode = None):
        super().__init__(
            Locator(f".//div[contains(@class,'element-group')]"
                    f"[.//div[contains(@class,'header-text') and .='{title}']]"),
            parent=parent,
            name=parameterize(title, separator="_"),
            valid_count=1,
        )
        self.title = title

    @overrides
    def init_node(self) -> None:
        super().init_node()

        # title
        GenericNode(Locator("div.header-text"), parent=self, name="title", valid_count=1)

        # element list
        GenericNode(Locator("div.element-list.show"), parent=self, name="element_list")

    @overrides
    def init_named_nodes(self) -> None:
        self.nn_title = self.find_node("title")
        self.nn_element_list = self.find_node("element_list")

    @property
    def is_expanded(self) -> bool:
        return self.nn_element_list.is_visible()

    @is_expanded.setter
    def is_expanded(self, value: bool) -> None:
        if self.is_expanded != value:
            self.nn_title.click()

    def select_sub_element(self, name: str) -> None:
        element_list = self.nn_element_list

        class SubElement(GenericNode):
            @overrides
            def __init__(self, sub_element: str) -> None:
                super().__init__(
                    Locator(f".//ul[contains(@class,'menu-list')]/li[contains(@class,'btn')][.='{sub_element}']"),
                    parent=element_list,
                )
                self.sub_element = sub_element

        self.is_expanded = True

        element = SubElement(name)
        element.click()
        element.parent = None


class WebConceptPage(GenericNode):
    default_name = "toolsqa_web_concept"

    @overrides
    def init_node(self) -> None:
        super().init_node()

        # page title
        GenericNode(Locator(".//div[contains(@class,'main-header')]"), parent=self, name="page_title", valid_count=1)

        # left pannel
        left_pannel = GenericNode(Locator("div.left-pannel"), parent=self, name="left_pannel", valid_count=1)
        AccordionElement("Elements", parent=left_pannel)
        AccordionElement("Forms", parent=left_pannel)
        AccordionElement("Alerts, Frame & Windows", parent=left_pannel)
        AccordionElement("Widgets", parent=left_pannel)
        AccordionElement("Interactions", parent=left_pannel)
        AccordionElement("Book Store Application", parent=left_pannel)

    @overrides
    def init_named_nodes(self) -> None:
        self.nn_page_title = self.find_node("page_title")
        self.nn_left_pannel = self.find_node("left_pannel")
        self.nn_left_pannel__elements = self.find_node("left_pannel__elements")
        self.nn_left_pannel__elements__title = self.find_node("left_pannel__elements__title")
        self.nn_left_pannel__elements__element_list = self.find_node("left_pannel__elements__element_list")
        self.nn_left_pannel__forms = self.find_node("left_pannel__forms")
        self.nn_left_pannel__forms__title = self.find_node("left_pannel__forms__title")
        self.nn_left_pannel__forms__element_list = self.find_node("left_pannel__forms__element_list")
        self.nn_left_pannel__alerts_frame_windows = self.find_node("left_pannel__alerts_frame_windows")
        self.nn_left_pannel__alerts_frame_windows__title = self.find_node("left_pannel__alerts_frame_windows__title")
        self.nn_left_pannel__alerts_frame_windows__element_list = self.find_node(
            "left_pannel__alerts_frame_windows__element_list")
        self.nn_left_pannel__widgets = self.find_node("left_pannel__widgets")
        self.nn_left_pannel__widgets__title = self.find_node("left_pannel__widgets__title")
        self.nn_left_pannel__widgets__element_list = self.find_node("left_pannel__widgets__element_list")
        self.nn_left_pannel__interactions = self.find_node("left_pannel__interactions")
        self.nn_left_pannel__interactions__title = self.find_node("left_pannel__interactions__title")
        self.nn_left_pannel__interactions__element_list = self.find_node("left_pannel__interactions__element_list")
        self.nn_left_pannel__book_store_application = self.find_node("left_pannel__book_store_application")
        self.nn_left_pannel__book_store_application__title = self.find_node(
            "left_pannel__book_store_application__title")
        self.nn_left_pannel__book_store_application__element_list = self.find_node(
            "left_pannel__book_store_application__element_list")
