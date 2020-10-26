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

        if isinstance(selectors_list, web_node.WebNode):
            selectors_list.wait_until_visible(timeout, raise_error=False)
            selectors_list = selectors_list.web_elements(only_visible=True)

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
                selector.is_displayed()
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

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_present(settings.MINI_TIMEOUT, raise_error=False)
            selector = selector.web_elements()

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

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_present(settings.MINI_TIMEOUT, raise_error=False)
            selector = selector.web_elements()

        if isinstance(selector, list):
            for s in selector:
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                    use_css=True,
                )
                super(PomBaseCase, self).remove_attributes(new_selector, attribute, new_by)
            return

        return super(PomBaseCase, self).remove_attributes(selector, attribute, by)

    def get_property_value(self, selector, property, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).get_property_value(selector, property, by, timeout)

    def get_image_url(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).get_image_url(selector, by, timeout)

    def find_elements(self, selector, by=By.CSS_SELECTOR, limit=0):
        if isinstance(selector, web_node.WebNode):
            selector.wait_until_present(settings.MINI_TIMEOUT, raise_error=False)
            elements = selector.web_elements()
            if limit > 0:
                elements = elements[:limit]
            return elements
        return super(PomBaseCase, self).find_elements(selector, by, limit)

    def find_visible_elements(self, selector, by=By.CSS_SELECTOR, limit=0):
        if isinstance(selector, web_node.WebNode):
            selector.wait_until_visible(settings.MINI_TIMEOUT, raise_error=False)
            elements = selector.web_elements(only_visible=True)
            if limit > 0:
                elements = elements[:limit]
            return elements
        return super(PomBaseCase, self).find_visible_elements(selector, by, limit)

    def click_visible_elements(self, selector, by=By.CSS_SELECTOR, limit=0, timeout=None):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            selector = selector.get_multiple_instances()
            selector = [s for s in selector if s.is_visible() is True]
            if limit > 0:
                selector = selector[:limit]

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_visible(timeout, raise_error=False)
            selector = selector.web_elements(only_visible=True)
            if limit > 0:
                selector = selector[:limit]

        if isinstance(selector, list):
            if limit > 0:
                selector = selector[:limit]
            for s in selector:
                assert isinstance(s, (web_node.WebNode, WebElement)), f"Invalid element type: {s}"
                if isinstance(s, web_node.WebNode) and s.is_visible() is False:
                    continue
                if isinstance(s, WebElement) and s.is_displayed() is False:
                    continue
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    timeout,
                    default_timeout=settings.SMALL_TIMEOUT,
                    required_visible=True,
                    use_css=True,
                )
                super(PomBaseCase, self).click(new_selector, new_by, timeout)
            return

        return super(PomBaseCase, self).click_visible_elements(selector, by, limit, timeout)

    def click_nth_visible_element(self, selector, number, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            instances = selector.get_multiple_instances()
            instances = [i for i in instances if i.is_visible() is True]
            selector = instances[number]

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_visible(timeout, raise_error=False)
            selector = selector.web_elements(only_visible=True)[number]

        if isinstance(selector, list):
            new_selector_list = []
            for s in selector:
                assert isinstance(s, (web_node.WebNode, WebElement)), f"Invalid element type: {s}"
                if isinstance(s, web_node.WebNode) and s.is_visible() is False:
                    continue
                if isinstance(s, WebElement) and s.is_displayed() is False:
                    continue
                new_selector, _ = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    timeout,
                    default_timeout=settings.SMALL_TIMEOUT,
                    required_visible=True,
                    use_css=True,
                )
                new_selector_list.append(new_selector)
            return self.click(new_selector_list[number])

        return super(PomBaseCase, self).click_nth_visible_element(selector, number, by, timeout)

    def click_if_visible(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).click_if_visible(selector, by)

    def is_checked(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).is_checked(selector, by, timeout)

    # def is_selected(self, selector, by=By.CSS_SELECTOR, timeout=None):
    # Same as is_checked()

    def check_if_unchecked(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).check_if_unchecked(selector, by)

    # def select_if_unselected(self, selector, by=By.CSS_SELECTOR):
    # Same as check_if_unchecked()

    def uncheck_if_checked(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).uncheck_if_checked(selector, by)

    # def unselect_if_selected(self, selector, by=By.CSS_SELECTOR):
    # Same as uncheck_if_checked()

    def is_element_in_an_iframe(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).is_element_in_an_iframe(selector, by)

    def switch_to_frame_of_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).switch_to_frame_of_element(selector, by)

    def hover_on_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).hover_on_element(selector, by)

    def hover_and_click(self,
                        hover_selector,
                        click_selector,
                        hover_by=By.CSS_SELECTOR,
                        click_by=By.CSS_SELECTOR,
                        timeout=None):
        if isinstance(hover_selector, (web_node.WebNode, WebElement)):
            self.hover_on_element(hover_selector)

        hover_selector, hover_by = self._get_selector_by_tuple_for_base(
            hover_selector,
            hover_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        click_selector, click_by = self._get_selector_by_tuple_for_base(
            click_selector,
            click_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).hover_and_click(hover_selector, click_selector, hover_by, click_by, timeout)

    def hover_and_double_click(self,
                               hover_selector,
                               click_selector,
                               hover_by=By.CSS_SELECTOR,
                               click_by=By.CSS_SELECTOR,
                               timeout=None):
        if isinstance(hover_selector, (web_node.WebNode, WebElement)):
            self.hover_on_element(hover_selector)

        hover_selector, hover_by = self._get_selector_by_tuple_for_base(
            hover_selector,
            hover_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        click_selector, click_by = self._get_selector_by_tuple_for_base(
            click_selector,
            click_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).hover_and_double_click(
            hover_selector, click_selector, hover_by, click_by, timeout,
        )

    def drag_and_drop(self,
                      drag_selector,
                      drop_selector,
                      drag_by=By.CSS_SELECTOR,
                      drop_by=By.CSS_SELECTOR,
                      timeout=None):

        drag_selector, drag_by = self._get_selector_by_tuple_for_base(
            drag_selector,
            drag_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        drop_selector, drop_by = self._get_selector_by_tuple_for_base(
            drop_selector,
            drop_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).drag_and_drop(drag_selector, drop_selector, drag_by, drop_by, timeout)

    def select_option_by_text(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR, timeout=None):
        dropdown_selector, dropdown_by = self._get_selector_by_tuple_for_base(
            dropdown_selector,
            dropdown_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).select_option_by_text(dropdown_selector, option, dropdown_by, timeout)

    def select_option_by_index(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR, timeout=None):
        dropdown_selector, dropdown_by = self._get_selector_by_tuple_for_base(
            dropdown_selector,
            dropdown_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).select_option_by_index(dropdown_selector, option, dropdown_by, timeout)

    def select_option_by_value(self, dropdown_selector, option, dropdown_by=By.CSS_SELECTOR, timeout=None):
        dropdown_selector, dropdown_by = self._get_selector_by_tuple_for_base(
            dropdown_selector,
            dropdown_by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).select_option_by_value(dropdown_selector, option, dropdown_by, timeout)

    def switch_to_frame(self, frame, timeout=None):
        if isinstance(frame, web_node.WebNode):
            frame = frame.wait_until_present(timeout)
        return super(PomBaseCase, self).switch_to_frame(frame, timeout)

    def bring_to_front(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).bring_to_front(selector, by)

    def highlight_click(self, selector, by=By.CSS_SELECTOR, loops=3, scroll=True):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).highlight_click(selector, by, loops, scroll)

    def highlight_update_text(self, selector, text, by=By.CSS_SELECTOR, loops=3, scroll=True):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).highlight_update_text(selector, text, by, loops, scroll)

    def highlight(self, selector, by=By.CSS_SELECTOR, loops=None, scroll=True):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).highlight(selector, by, loops, scroll)

    def press_up_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).press_up_arrow(selector, times, by)

    def press_down_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).press_down_arrow(selector, times, by)

    def press_left_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).press_left_arrow(selector, times, by)

    def press_right_arrow(self, selector="html", times=1, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).press_right_arrow(selector, times, by)

    def scroll_to(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).scroll_to(selector, by, timeout)

    def slow_scroll_to(self, selector, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).slow_scroll_to(selector, by, timeout)

    def js_click(self, selector, by=By.CSS_SELECTOR, all_matches=False):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            if all_matches is True:
                selector = selector.get_multiple_instances()
            else:
                selector = selector.wait_until_visible()

        if isinstance(selector, web_node.WebNode):
            new_selector = selector.wait_until_visible(settings.MINI_TIMEOUT)
            if all_matches is True:
                new_selector = selector.web_elements(only_visible=True)
            selector = new_selector

        if isinstance(selector, list):
            for s in selector:
                assert isinstance(s, (web_node.WebNode, WebElement)), f"Invalid element type: {s}"
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                    required_visible=True,
                )
                super(PomBaseCase, self).js_click(new_selector, new_by, all_matches)
            return

        return super(PomBaseCase, self).js_click(selector, by, all_matches)

    # def js_click_all(self, selector, by=By.CSS_SELECTOR):
    # Same as js_click() with all_matches=True

    def jquery_click(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).jquery_click(selector, by)

    def jquery_click_all(self, selector, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            selector = selector.get_multiple_instances()

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_visible(settings.MINI_TIMEOUT)
            selector = selector.web_elements(only_visible=True)

        if isinstance(selector, list):
            for s in selector:
                assert isinstance(s, (web_node.WebNode, WebElement)), f"Invalid element type: {s}"
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                    required_visible=True,
                )
                super(PomBaseCase, self).jquery_click_all(new_selector, new_by)
            return

        return super(PomBaseCase, self).jquery_click_all(selector, by)

    def hide_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).hide_element(selector, by)

    def hide_elements(self, selector, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            selector = selector.get_multiple_instances()

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_present(settings.MINI_TIMEOUT)
            selector = selector.web_elements()

        if isinstance(selector, list):
            for s in selector:
                assert isinstance(s, (web_node.WebNode, WebElement)), f"Invalid element type: {s}"
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                )
                super(PomBaseCase, self).hide_elements(new_selector, new_by)
            return

        return super(PomBaseCase, self).hide_elements(selector, by)

    def show_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).show_element(selector, by)

    def show_elements(self, selector, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            selector = selector.get_multiple_instances()

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_present(settings.MINI_TIMEOUT)
            selector = selector.web_elements()

        if isinstance(selector, list):
            for s in selector:
                assert isinstance(s, (web_node.WebNode, WebElement)), f"Invalid element type: {s}"
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                )
                super(PomBaseCase, self).show_elements(new_selector, new_by)
            return

        return super(PomBaseCase, self).show_elements(selector, by)

    def remove_element(self, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).remove_element(selector, by)

    def remove_elements(self, selector, by=By.CSS_SELECTOR):
        if isinstance(selector, web_node.WebNode) and selector.is_multiple is True:
            selector = selector.get_multiple_instances()

        if isinstance(selector, web_node.WebNode):
            selector.wait_until_present(settings.MINI_TIMEOUT)
            selector = selector.web_elements()

        if isinstance(selector, list):
            for s in selector:
                assert isinstance(s, (web_node.WebNode, WebElement)), f"Invalid element type: {s}"
                new_selector, new_by = self._get_selector_by_tuple_for_base(
                    s,
                    by,
                    settings.MINI_TIMEOUT,
                    default_timeout=settings.MINI_TIMEOUT,
                )
                super(PomBaseCase, self).remove_elements(new_selector, new_by)
            return

        return super(PomBaseCase, self).remove_elements(selector, by)

    def choose_file(self, selector, file_path, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).choose_file(selector, file_path, by, timeout)

    def save_element_as_image_file(self, selector, file_name, folder=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            By.CSS_SELECTOR,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).save_element_as_image_file(selector, file_name, folder)

    def set_value(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).set_value(selector, text, by, timeout)

    def js_update_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).js_update_text(selector, text, by, timeout)

    def js_type(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).js_type(selector, text, by, timeout)

    def set_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).set_text(selector, text, by, timeout)

    def jquery_update_text(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).jquery_update_text(selector, text, by, timeout)

    def input(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).input(selector, text, by, timeout, retry)

    def write(self, selector, text, by=By.CSS_SELECTOR, timeout=None, retry=False):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).write(selector, text, by, timeout, retry)

    def send_keys(self, selector, text, by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).send_keys(selector, text, by, timeout)

    def wait_for_element_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_visible(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).wait_for_element_visible(selector, by, timeout)

    def wait_for_element_not_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_not_present(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).wait_for_element_not_present(selector, by, timeout)

    def assert_element_not_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_not_present(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).assert_element_not_present(selector, by, timeout)

    def add_tour_step(self, message, selector=None, name=None, title=None, theme=None, alignment=None, duration=None):
        selector, _ = self._get_selector_by_tuple_for_base(
            selector,
            By.CSS_SELECTOR,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
        )
        return super(PomBaseCase, self).add_tour_step(message, selector, name, title, theme, alignment, duration)

    def post_message_and_highlight(self, message, selector, by=By.CSS_SELECTOR):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            settings.MINI_TIMEOUT,
            default_timeout=settings.MINI_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).post_message_and_highlight(message, selector, by)

    def wait_for_element_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_present(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).wait_for_element_present(selector, by, timeout)

    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_visible(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).wait_for_element(selector, by, timeout)

    def get_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_present(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).get_element(selector, by, timeout)

    def assert_element_present(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            selector.wait_until_present(timeout)
            return
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
        )
        return super(PomBaseCase, self).assert_element_present(selector, by, timeout)

    def find_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_visible(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).find_element(selector, by, timeout)

    def assert_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            selector.wait_until_visible(timeout)
            return
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).assert_element(selector, by, timeout)

    def assert_element_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            selector.wait_until_visible(timeout)
            return
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.SMALL_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).assert_element_visible(selector, by, timeout)

    def wait_for_text_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).wait_for_text_visible(text, selector, by, timeout)

    def wait_for_exact_text_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).wait_for_exact_text_visible(text, selector, by, timeout)

    def wait_for_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).wait_for_text(text, selector, by, timeout)

    def find_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).find_text(text, selector, by, timeout)

    def assert_text_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).assert_text_visible(text, selector, by, timeout)

    def assert_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).assert_text(text, selector, by, timeout)

    def assert_exact_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
            required_visible=True,
        )
        return super(PomBaseCase, self).assert_exact_text(text, selector, by, timeout)

    def wait_for_element_absent(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_not_present(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).wait_for_element_absent(selector, by, timeout)

    def assert_element_absent(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_not_present(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).assert_element_absent(selector, by, timeout)

    def wait_for_element_not_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_not_visible(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).wait_for_element_not_visible(selector, by, timeout)

    def assert_element_not_visible(self, selector, by=By.CSS_SELECTOR, timeout=None):
        if isinstance(selector, web_node.WebNode):
            return selector.wait_until_not_visible(timeout)
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).assert_element_not_visible(selector, by, timeout)

    def wait_for_text_not_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).wait_for_text_not_visible(text, selector, by, timeout)

    def assert_text_not_visible(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
        selector, by = self._get_selector_by_tuple_for_base(
            selector,
            by,
            timeout,
            default_timeout=settings.LARGE_TIMEOUT,
        )
        return super(PomBaseCase, self).assert_text_not_visible(text, selector, by, timeout)

    # def deferred_assert_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
    # Do not know how to add support to WebNode or WebElement

    # def deferred_assert_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
    # Do not know how to add support to WebNode or WebElement

    # def delayed_assert_element(self, selector, by=By.CSS_SELECTOR, timeout=None):
    # Do not know how to add support to WebNode or WebElement

    # def delayed_assert_text(self, text, selector="html", by=By.CSS_SELECTOR, timeout=None):
    # Do not know how to add support to WebNode or WebElement
