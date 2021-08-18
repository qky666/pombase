from __future__ import annotations

from inflection import parameterize
from overrides import overrides
from pombase.web_node import WebNode, Locator
from pages.toolsqa.toolsqa_page import ToolsQAPage


class HomePage(ToolsQAPage):
    default_name = "toolsqa_home"

    @overrides
    def init_node(self) -> None:
        super().init_node()

        # cards
        cards = WebNode(Locator("div.category-cards"), parent=self, name="cards", valid_count=1)

        class Card(WebNode):
            @overrides
            def __init__(self, card: str) -> None:
                super().__init__(
                    Locator(f".//div[contains(concat(' ',normalize-space(@class),' '),' card ')][.='{card}']"),
                    parent=cards,
                    name=parameterize(card, separator="_"),
                    valid_count=1)
                self.card = card

        Card("Elements")
        Card("Forms")
        Card("Alerts, Frame & Windows")
        Card("Widgets")
        Card("Interactions")
        Card("Book Store Application")

    @overrides
    def init_named_nodes(self) -> None:
        self.nn_header = self.find_node("header")
        self.nn_header__logo = self.find_node("header__logo")
        self.nn_cards = self.find_node("cards")
        self.nn_cards__elements = self.find_node("cards__elements")
        self.nn_cards__forms = self.find_node("cards__forms")
        self.nn_cards__alerts_frame_windows = self.find_node("cards__alerts_frame_windows")
        self.nn_cards__widgets = self.find_node("cards__widgets")
        self.nn_cards__interactions = self.find_node("cards__interactions")
        self.nn_cards__book_store_application = self.find_node("cards__book_store_application")
