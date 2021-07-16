from __future__ import annotations
import typing
import collections
import functools
import selenium.webdriver.common.by as selenium_by
import cssselect.xpath as css_xpath

import pombase.util as util
import pombase.web_node as web_node

SelectorByTuple = collections.namedtuple("SelectorByTuple", "selector by")


class Locator:

    translator = css_xpath.GenericTranslator()

    def __init__(self, selector: str, by: str = None, index: int = None) -> None:
        assert len(selector) > 0, \
            f"Validation error. Locator.selector should not be empty: selector={selector}"
        self._selector = selector
        self._by = by
        self._index = index

    def __repr__(self):
        return f"Locator(_selector={self._selector}, _by={self._by}, _index={self._index})"

    def copy(self, selector: str = None, by: str = None, index: int = None) -> Locator:
        return Locator(
            selector=util.first_not_none(selector, self._selector),
            by=util.first_not_none(by, self._by),
            index=util.first_not_none(index, self._index),
        )

    @property
    def selector(self) -> str:
        if self._index is not None:
            xpath = as_xpath(self._selector, self._by)
            return f"({xpath})[{self._index + 1}]"
        return self._selector

    @property
    def by(self) -> str:
        if self._index is not None:
            return selenium_by.By.XPATH
        elif self._by is not None:
            return self._by
        else:
            return infer_by_from_selector(self._selector)

    @property
    def index(self) -> typing.Optional[int]:
        return self._index

    def as_css_selector(self) -> typing.Optional[str]:
        if self.index is not None:
            return None
        else:
            return as_css(self.selector, self.by)

    def as_xpath_selector(self) -> str:
        if self.index is not None:
            return self.selector
        else:
            return as_xpath(self.selector, self.by)

    def as_selector_by_tuple(self) -> SelectorByTuple:
        return SelectorByTuple(self.selector, self.by)

    def __eq__(self, other: typing.Any) -> bool:
        try:
            other = get_locator(other)
        except TypeError:
            return False
        except AssertionError:
            return False
        if other.selector == self.selector and other.by == self.by:
            return True
        else:
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


PseudoLocator = typing.Union[Locator, str, dict, typing.Iterable, web_node.WebNode]


def as_css(selector: str, by: str = None) -> typing.Optional[str]:
    if by is None:
        by = infer_by_from_selector(selector)
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


def as_xpath(selector: str, by: str = None) -> str:
    if by is None:
        by = infer_by_from_selector(selector)
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


def compound(locator: PseudoLocator, *args: PseudoLocator) -> Locator:
    locators = [locator] + list(args)
    locators: typing.List[Locator] = [get_locator(loc) for loc in locators]
    return functools.reduce(lambda l1, l2: l1.append(l2), locators)


def infer_by_from_selector(selector: str) -> str:
    if selector == "." \
            or selector.startswith("./") \
            or selector.startswith("/") \
            or selector.startswith("("):
        return selenium_by.By.XPATH
    else:
        return selenium_by.By.CSS_SELECTOR


def get_locator(obj: PseudoLocator) -> Locator:
    if isinstance(obj, Locator):
        return obj
    elif isinstance(obj, web_node.WebNode):
        return obj.locator
    elif isinstance(obj, str):
        return Locator(obj)
    elif isinstance(obj, dict):
        return Locator(**obj)
    elif isinstance(obj, typing.Iterable):
        return Locator(*obj)
    else:
        assert False, f"Can not get object as a Locator: {obj}"
