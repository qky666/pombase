from __future__ import annotations

import typing

from seleniumbase.fixtures.base_case import BaseCase
from seleniumbase.fixtures.page_actions import timeout_exception
from seleniumbase.config import settings

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from . import web_node
from . import util
from . import base_settings


class PomBaseCase(BaseCase):

    def _get_selector_by_tuple_for_base(self,
                                        selector: typing.Union[str, WebElement, web_node.WebNode],
                                        by: str,
                                        timeout: typing.Union[int, float],
                                        default_timeout: typing.Union[int, float],
                                        required_visible: bool = False,
                                        use_css: bool = False,
                                        ) -> typing.Tuple[str, str]:
        node = None
        if isinstance(selector, web_node.WebNode):
            node = selector
            if required_visible is True:
                selector = selector.wait_until_visible(timeout=timeout)
            else:
                selector = selector.wait_until_present(timeout=timeout)
        if isinstance(selector, WebElement):
            if required_visible is True:
                assert selector.is_displayed() is True, \
                    f"WebElement should be visible, but it is not. WebElement: {selector}"
            if use_css is True:
                css = getattr(selector, util.Util.CANONICAL_CSS, None)
                if css is None:
                    selector = util.Util.attach_canonical_xpath_css_and_node_to_web_element(selector, node)
                    if selector is None:
                        timeout = base_settings.BaseSettings.apply_timeout_multiplier(self, default_timeout)
                        plural = "s"
                        if timeout == 1 or timeout == 1.0:
                            plural = ""
                        message = f"WebElement was not present after {timeout} second{plural}: {selector}"
                        timeout_exception(NoSuchElementException, message)
                    if required_visible is True:
                        assert selector.is_displayed() is True, \
                            f"WebElement should be visible, but it is not. WebElement: {selector}"
                    css = getattr(selector, util.Util.CANONICAL_CSS)
                selector = css
                by = By.CSS_SELECTOR
            else:
                xpath = getattr(selector, util.Util.CANONICAL_XPATH, None)
                if xpath is None:
                    selector = util.Util.attach_canonical_xpath_css_and_node_to_web_element(selector, node)
                    if selector is None:
                        timeout = base_settings.BaseSettings.apply_timeout_multiplier(self, default_timeout)
                        plural = "s"
                        if timeout == 1 or timeout == 1.0:
                            plural = ""
                        message = f"WebElement was not present after {timeout} second{plural}: {selector}"
                        timeout_exception(NoSuchElementException, message)
                    if required_visible is True:
                        assert selector.is_displayed() is True, \
                            f"WebElement should be visible, but it is not. WebElement: {selector}"
                    xpath = getattr(selector, util.Util.CANONICAL_XPATH)
                selector = xpath
                by = By.XPATH
        return selector, by

    def click(self, selector, by=By.CSS_SELECTOR, timeout=None, delay=0):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).click(selector, by, timeout, delay)

    def slow_click(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).click(selector, by, timeout)

    def double_click(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).double_click(selector, by, timeout)

    def click_chain(self, selectors_list, by=By.CSS_SELECTOR, timeout=None, spacing=0):
        if isinstance(selectors_list, web_node.WebNode) and selectors_list.is_multiple is True:
            selectors_list = selectors_list.get_multiple_instances()

        new_selector_list = []
        for selector in selectors_list:
            new_selector, _ = self._get_selector_by_tuple_for_base(
                selector,
                by,
                timeout,
                default_timeout=settings.SMALL_TIMEOUT,
                required_visible=True,
                use_css=True,
            )
            new_selector_list.append(new_selector)
        return super(PomBaseCase, self).click_chain(new_selector_list, by, timeout, spacing)

    def update_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).update_text(selector, by, timeout, retry)

    def add_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).add_text(selector, text, by, timeout)

    def type(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).type(selector, text, by, timeout, retry)

    def submit(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.SMALL_TIMEOUT,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).submit(selector, by)

    def clear(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).clear(selector, by, timeout)

    def is_element_present(self, selector, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode):
            return selector.is_present()
        if isinstance(selector, WebElement):
            try:
                tag = selector.tag_name
                if tag is not None:
                    return True
            except StaleElementReferenceException:
                return False
        return super(PomBaseCase, self).is_element_present(selector, by)

    def is_element_visible(self, selector, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode):
            return selector.is_visible()
        if isinstance(selector, WebElement):
            try:
                visible = selector.is_displayed()
                if visible is True:
                    return True
                else:
                    return False
            except StaleElementReferenceException:
                return False
        return super(PomBaseCase, self).is_element_visible(selector, by)

    def is_text_visible(self, text, selector="html", by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).is_text_visible(text, selector, by)

    def get_text(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).get_text(selector, by, timeout)

    def get_attribute(self, selector, attribute, by=By.CSS_SELECTOR, timeout=None, hard_fail=True):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).get_attribute(selector, attribute, by, timeout, hard_fail)

    def set_attribute(self, selector, attribute, value, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).set_attribute(selector, attribute, value, by, timeout)

    def set_attributes(self, selector, attribute, value, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            selector = selector.get_multiple_instances()

        if isinstance(selector, list):
            for s in selector:
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                    use_css=True,
                )
                super(PomBaseCase, self).set_attributes(new_selector, attribute, value, new_by)
            return

        return super(PomBaseCase, self).set_attributes(selector, attribute, value, by)

    # def set_attribute_all(self, selector, attribute, value, by=By.CSS_SELECTOR):
    # Same as set_attributes()

    def remove_attribute(self, selector, attribute, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).remove_attribute(selector, attribute, by, timeout)

    def remove_attributes(self, selector, attribute, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            selector = selector.get_multiple_instances()

        if isinstance(selector, list):
            for s in selector:
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                    use_css=True,
                )
                super(PomBaseCase, self).remove_attribute(new_selector, attribute, new_by)
            return

        return super(PomBaseCase, self).remove_attributes(selector, attribute, by)
