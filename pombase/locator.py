from __future__ import annotations
import typing
import collections
import selenium.webdriver.common.by as selenium_by
import cssselect.xpath as css_xpath

import pombase.util as util

SelectorByTuple = collections.namedtuple("SelectorByTuple", "selector by")


class Locator:

    translator = css_xpath.GenericTranslator()

    def __init__(self, selector: str, by: str = None, index: int = None) -> None:
        self._selector = selector
        self._by = by
        self._index = index

    def copy(self, selector: str = None, by: str = None, index: int = None) -> Locator:
        return Locator(
            selector=util.first_not_none(selector, self._selector),
            by=util.first_not_none(by, self._by),
            index=util.first_not_none(index, self._index),
        )

    @property
    def selector(self) -> str:
        if self._index is not None:
            xpath = Locator.as_xpath(self._selector, self._by)
            return f"({xpath})[{self._index + 1}]"
        return self._selector

    @property
    def by(self) -> str:
        if self._index is not None:
            return selenium_by.By.XPATH
        elif self._by is not None:
            return self._by
        else:
            return self.infer_by_from_selector(self._selector)

    @property
    def index(self) -> typing.Optional[int]:
        return self._index

    @staticmethod
    def infer_by_from_selector(selector: str) -> str:
        if selector == "." \
                or selector.startswith("./") \
                or selector.startswith("/") \
                or selector.startswith("("):
            return selenium_by.By.XPATH
        else:
            return selenium_by.By.CSS_SELECTOR

    @staticmethod
    def as_css(selector: str, by: str = None) -> typing.Optional[str]:
        if by is None:
            by = Locator.infer_by_from_selector(selector)
        if by == selenium_by.By.ID:
            return f"#{selector}"
        elif by == selenium_by.By.XPATH:
            return None
        elif by == selenium_by.By.LINK_TEXT:
            return None
        elif by == selenium_by.By.PARTIAL_LINK_TEXT:
            return None
        elif by == selenium_by.By.NAME:
            return f"[name='{selector}']"
        elif by == selenium_by.By.TAG_NAME:
            return selector
        elif by == selenium_by.By.CLASS_NAME:
            return f".{selector}"
        elif by == selenium_by.By.CSS_SELECTOR:
            return selector
        else:
            assert False, f"Unknown 'by': {by}"

    @staticmethod
    def as_xpath(selector: str, by: str = None) -> str:
        if by is None:
            by = Locator.infer_by_from_selector(selector)
        if by == selenium_by.By.ID:
            return f".//*[@id='{selector}']"
        elif by == selenium_by.By.XPATH:
            return selector
        elif by == selenium_by.By.LINK_TEXT:
            return f".//a[normalize-space(.)='{selector}']"
        elif by == selenium_by.By.PARTIAL_LINK_TEXT:
            return f".//a[contains(normalize-space(.),'{selector}')]"
        elif by == selenium_by.By.NAME:
            return f".//*[@name='{selector}']"
        elif by == selenium_by.By.TAG_NAME:
            return f".//{selector}"
        elif by == selenium_by.By.CLASS_NAME:
            return f".//*[contains(concat(' ',normalize-space(@class),' '),' {selector} ')]"
        elif by == selenium_by.By.CSS_SELECTOR:
            return Locator.translator.css_to_xpath(selector, ".//")
        else:
            assert False, f"Unknown 'by': {by}"

    def as_css_selector(self) -> typing.Optional[str]:
        if self.index is not None:
            return None
        else:
            return Locator.as_css(self.selector, self.by)

    def as_xpath_selector(self) -> str:
        if self.index is not None:
            return self.selector
        else:
            return Locator.as_xpath(self.selector, self.by)

    def as_selector_by_tuple(self) -> SelectorByTuple:
        return SelectorByTuple(self.selector, self.by)

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, str):
            other = (other, None, None)
        if isinstance(other, tuple) \
                and len(other) == 2 \
                and isinstance(other[0], str) \
                and isinstance(other[1], (str, type(None))):
            other = (other[0], other[1], None)
        if isinstance(other, tuple) \
                and len(other) == 2 \
                and isinstance(other[0], str) \
                and isinstance(other[1], int):
            other = (other[0], None, other[1])
        if isinstance(other, tuple) \
                and len(other) == 3 \
                and isinstance(other[0], str) \
                and isinstance(other[1], (str, type(None))) \
                and isinstance(other[2], (int, type(None))):
            other = Locator(*other)
        if isinstance(other, Locator):
            if other.selector == self.selector and other.by == self.by:
                return True
        return False

    def append(self, locator: Locator) -> Locator:
        self_as_css = self.as_css_selector()
        locator_as_css = locator.as_css_selector()
        if self_as_css is not None and locator_as_css is not None:
            return Locator(f"{self_as_css} {locator_as_css}")
        else:
            self_as_xpath = self.as_xpath_selector()
            locator_as_xpath = locator.as_xpath_selector()
            xpath = self_as_xpath
            if locator_as_xpath.startswith("/"):
                # Reset xpath
                xpath = ""
            else:
                if locator_as_xpath.startswith("("):
                    # Put "(" in the beginning
                    xpath = f"({xpath}"
                    locator_as_xpath = locator_as_xpath[1:]
                if locator_as_xpath.startswith("."):
                    # Remove "."
                    locator_as_xpath = locator_as_xpath[1:]
            xpath = f"{xpath}{locator_as_xpath}"
            return Locator(xpath)

    @staticmethod
    def compound(*args) -> Locator:
        assert len(args) > 0, f"Locator list is empty"
        locators = [arg if isinstance(arg, Locator) else Locator(arg) for arg in args]
        prev_locator = locators[0]
        for locator in locators[1:]:
            prev_locator = prev_locator.append(locator)
        return prev_locator
