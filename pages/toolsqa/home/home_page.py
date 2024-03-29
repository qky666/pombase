from __future__ import annotations

from overrides import overrides
from pombase import SingleWebNode
from pages.toolsqa.toolsqa_page import ToolsQAPage


class Card(SingleWebNode):
    @overrides(check_signature=False)
    def __init__(self, title: str) -> None:
        self.title = title
        super().__init__(
            f".//div[contains(concat(' ',normalize-space(@class),' '),' card ')][.='{title}']",
            required=True)


class HomePage(ToolsQAPage):
    @overrides
    def init_node(self) -> None:
        super().init_node()

        # cards
        self.swn_cards = SingleWebNode("div.category-cards", required=True)
        self.swn_cards__swn_elements = Card("Elements")
        self.swn_cards__swn_forms = Card("Forms")
        self.swn_cards__swn_alerts_frame_windows = Card("Alerts, Frame & Windows")
        self.swn_cards__swn_widgets = Card("Widgets")
        self.swn_cards__swn_interactions = Card("Interactions")
        self.swn_cards__swn_book_store_application = Card("Book Store Application")
