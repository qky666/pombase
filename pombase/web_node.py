from __future__ import annotations

import anytree
import typing
import time
import os
import importlib
import inspect

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from selenium.webdriver.remote.errorhandler import ElementNotVisibleException

from seleniumbase.config import settings
from seleniumbase.fixtures import shared_utils as s_utils
from seleniumbase.fixtures.page_actions import timeout_exception

from . import pom_base_case as pbc
from . import util
from . import file_loader
from . import base_settings


class WebNode(anytree.node.anynode.AnyNode):

    def __init__(self,
                 *,
                 parent: WebNode = None,
                 children: typing.Iterable[WebNode] = None,
                 name: str = None,
                 locator: str = None,  # Allow "id=my_selector", etc.
                 order: int = None,
                 text_pattern: str = None,  # Allow * and ? (\*, \?)
                 ignore_case_in_text_pattern: bool = None,
                 use_regexp_in_text_pattern: bool = None,
                 override_parent_selector: typing.Union[str, bool] = None,  # If True, use "css selector=html"
                 should_be_present: bool = None,
                 should_be_visible: bool = None,
                 is_multiple: bool = None,
                 is_multiple_instance_from: typing.Union[str, WebNode] = None,
                 is_template: bool = None,
                 template: typing.Union[str, WebNode] = None,
                 template_args: list = None,
                 template_kwargs: dict = None,
                 pom_base_case: pbc.PomBaseCase = None,
                 desired_class_name: str = None,
                 **kwargs,
                 ):
        if template_args is None:
            template_args = []
        if template_kwargs is None:
            template_kwargs = {}

        self.parent: WebNode
        self.children: typing.Iterable[WebNode]
        self._name = name
        self._locator = locator
        self._order = order
        self._text_pattern = text_pattern
        self._ignore_case_in_text_pattern = ignore_case_in_text_pattern
        self._use_regexp_in_text_pattern = use_regexp_in_text_pattern
        self._override_parent_selector = override_parent_selector
        self._should_be_present = should_be_present
        self._should_be_visible = should_be_visible
        self._is_multiple = is_multiple
        self._is_multiple_instance_from = is_multiple_instance_from
        self._is_template = is_template
        self._template = template
        self._template_args = template_args
        self._template_kwargs = template_kwargs
        self._pom_base_case = pom_base_case
        self._desired_class_name = desired_class_name
        self._kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        super(WebNode, self).__init__(parent=parent, children=children)
        self.init_node()

    ############
    # Accessors
    ############
    # name
    @property
    def name(self) -> typing.Optional[str]:
        if self._name is None:
            if self.template is not None and self.template.name is not None:
                return self.template.name.format(*self.template_args, **self.template_kwargs)
        return self._name

    @name.setter
    def name(self, value: typing.Optional[str]) -> None:
        self._name = value
        self.validate()
        self.validate_unique_descendant_names()
        if self.is_root is False:
            parent: WebNode = self.parent
            parent.validate_unique_descendant_names()

    # locator
    @property
    def locator(self) -> str:
        if self._locator is None:
            if self.template is not None and self.template.locator is not None:
                return self.template.locator.format(*self.template_args, **self.template_kwargs)
            else:
                if self.is_root:
                    return "//html"
                else:
                    return "."
        return self._locator

    @locator.setter
    def locator(self, value: typing.Optional[str]) -> None:
        self._locator = value
        self.validate()

    # order
    @property
    def order(self) -> typing.Optional[int]:
        if self._order is None:
            if self.template is not None and self.template.order is not None:
                return self.template.order
        return self._order

    @order.setter
    def order(self, value: typing.Optional[int]) -> None:
        self._order = value
        self.validate()

    # text_pattern
    @property
    def text_pattern(self) -> typing.Optional[str]:
        if self._text_pattern is None:
            if self.template is not None and self.template.text_pattern is not None:
                return self.template.text_pattern.format(*self.template_args, **self.template_kwargs)
        return self._text_pattern

    @text_pattern.setter
    def text_pattern(self, value: typing.Optional[str]) -> None:
        self._text_pattern = value
        self.validate()

    # ignore_case_in_text_pattern
    @property
    def ignore_case_in_text_pattern(self) -> bool:
        if self._ignore_case_in_text_pattern is None:
            if self.template is not None and self.template.ignore_case_in_text_pattern is not None:
                return self.template.ignore_case_in_text_pattern
            return False
        return self._ignore_case_in_text_pattern

    @ignore_case_in_text_pattern.setter
    def ignore_case_in_text_pattern(self, value: typing.Optional[bool]) -> None:
        self._ignore_case_in_text_pattern = value
        self.validate()

    # use_regexp_in_text_pattern
    @property
    def use_regexp_in_text_pattern(self) -> bool:
        if self._use_regexp_in_text_pattern is None:
            if self.template is not None and self.template.use_regexp_in_text_pattern is not None:
                return self.template.use_regexp_in_text_pattern
            return False
        return self._use_regexp_in_text_pattern

    @use_regexp_in_text_pattern.setter
    def use_regexp_in_text_pattern(self, value: typing.Optional[bool]) -> None:
        self._use_regexp_in_text_pattern = value
        self.validate()

    # override_parent_selector
    @property
    def override_parent_selector(self) -> typing.Optional[str]:
        if self._override_parent_selector is None:
            if self.template is not None and self.template.override_parent_selector is not None:
                return self.template.override_parent_selector.format(*self.template_args, **self.template_kwargs)
        if self._override_parent_selector is True:
            return "//html"
        if self._override_parent_selector is False:
            return None
        return self._override_parent_selector

    @override_parent_selector.setter
    def override_parent_selector(self, value: typing.Union[str, bool, None]) -> None:
        self._override_parent_selector = value
        self.validate()

    # should_be_present
    @property
    def should_be_present(self) -> bool:
        if self._should_be_present is None:
            if self.template is not None and self.template.should_be_present is not None:
                return self.template.should_be_present
            if self.should_be_visible is True:
                return True
            else:
                return False
        return self._should_be_present

    @should_be_present.setter
    def should_be_present(self, value: typing.Optional[bool]) -> None:
        self._should_be_present = value
        self.validate()

    # should_be_visible
    @property
    def should_be_visible(self) -> bool:
        if self._should_be_visible is None:
            if self.template is not None and self.template.should_be_visible is not None:
                return self.template.should_be_visible
            return False
        return self._should_be_visible

    @should_be_visible.setter
    def should_be_visible(self, value: typing.Optional[bool]) -> None:
        self._should_be_visible = value
        self.validate()

    # is_multiple
    @property
    def is_multiple(self) -> bool:
        if self._is_multiple is None:
            if self.template is not None and self.template.is_multiple is not None:
                return self.template.is_multiple
            return False
        return self._is_multiple

    @is_multiple.setter
    def is_multiple(self, value: typing.Optional[bool]) -> None:
        self._is_multiple = value
        self.validate()

    # is_multiple_instance_from
    @property
    def is_multiple_instance_from(self) -> typing.Optional[WebNode]:
        if isinstance(self._is_multiple_instance_from, str):
            return self.get_node(self._is_multiple_instance_from, only_descendants=False)
        return self._is_multiple_instance_from

    @is_multiple_instance_from.setter
    def is_multiple_instance_from(self, value: typing.Union[str, WebNode, None]) -> None:
        self._is_multiple_instance_from = value
        self.validate()

    # is_template
    @property
    def is_template(self) -> bool:
        if self._is_template is None:
            return False
        return self._is_template

    @is_template.setter
    def is_template(self, value: typing.Optional[bool]) -> None:
        self._is_template = value
        self.validate()

    # template
    @property
    def template(self) -> typing.Optional[WebNode]:
        if isinstance(self._template, str):
            return self.get_node(self._template, only_descendants=False)
        return self._template

    @template.setter
    def template(self, value: typing.Union[str, WebNode, None]) -> None:
        self._is_template = value
        self.validate()

    # template_args
    @property
    def template_args(self) -> list:
        return self._template_args

    @template_args.setter
    def template_args(self, value: typing.Optional[list]) -> None:
        if value is None:
            self._template_args = []
        else:
            self._template_args = value
        self.validate()

    # template_kwargs
    @property
    def template_kwargs(self) -> dict:
        return self._template_kwargs

    @template_kwargs.setter
    def template_kwargs(self, value: typing.Optional[dict]) -> None:
        if value is None:
            self._template_kwargs = {}
        else:
            self._template_kwargs = value
        self.validate()

    # pom_base_case
    @property
    def pom_base_case(self) -> pbc.PomBaseCase:
        if self._pom_base_case is None:
            return self.root.pom_base_case
        return self._pom_base_case

    @pom_base_case.setter
    def pom_base_case(self, value: typing.Optional[pbc.PomBaseCase]) -> None:
        self._pom_base_case = value

    # desired_class_name
    @property
    def desired_class_name(self) -> typing.Optional[str]:
        return self._desired_class_name

    @desired_class_name.setter
    def desired_class_name(self, value: typing.Optional[str]) -> None:
        self._desired_class_name = value

    ######################
    # Computed properties
    ######################
    @property
    def relevant_properties(self) -> typing.Dict[str]:
        kwargs = {key: getattr(self, key) for key in self._kwargs}
        return dict(
            name=self._name,
            locator=self._locator,
            order=self._order,
            text_pattern=self._text_pattern,
            ignore_case_in_text_pattern=self._ignore_case_in_text_pattern,
            use_regexp_in_text_pattern=self._use_regexp_in_text_pattern,
            should_be_present=self._should_be_present,
            should_be_visible=self._should_be_visible,
            is_multiple=self._is_multiple,
            is_multiple_instance_from=self._is_multiple_instance_from,
            is_template=self._is_template,
            template=self._template,
            template_args=self._template_args,
            template_kwargs=self._template_kwargs,
            pom_base_case=self._pom_base_case,
            class_name=self._desired_class_name,
            **kwargs,
        )

    @property
    def object_id(self) -> int:
        return id(self)

    @property
    def full_name(self) -> str:
        full_name = ""
        for node in self.path:
            if node.name is not None:
                full_name = f"{full_name}{self.separator}{self.name}"
        if self.name is None:
            full_name = f"{full_name}{self.separator}{self.object_id}"
        return full_name

    @property
    def selector_by_tuple(self) -> typing.Tuple[str, str]:
        bys: typing.Dict[str, typing.List[str]] = {
            By.ID: [By.ID.casefold(),
                    By.ID.replace("_", " ").casefold(),
                    By.ID.replace(" ", "_").casefold()],
            By.XPATH: [By.XPATH.casefold(),
                       By.XPATH.replace("_", " ").casefold(),
                       By.XPATH.replace(" ", "_").casefold()],
            By.LINK_TEXT: [By.LINK_TEXT.casefold(),
                           By.LINK_TEXT.replace("_", " ").casefold(),
                           By.LINK_TEXT.replace(" ", "_").casefold()],
            By.PARTIAL_LINK_TEXT: [By.PARTIAL_LINK_TEXT.casefold(),
                                   By.PARTIAL_LINK_TEXT.replace("_", " ").casefold(),
                                   By.PARTIAL_LINK_TEXT.replace(" ", "_").casefold()],
            By.NAME: [By.NAME.casefold(),
                      By.NAME.replace("_", " ").casefold(),
                      By.NAME.replace(" ", "_").casefold()],
            By.TAG_NAME: [By.TAG_NAME.casefold(),
                          By.TAG_NAME.replace("_", " ").casefold(),
                          By.TAG_NAME.replace(" ", "_").casefold()],
            By.CLASS_NAME: [By.CLASS_NAME.casefold(),
                            By.CLASS_NAME.replace("_", " ").casefold(),
                            By.CLASS_NAME.replace(" ", "_").casefold()],
            By.CSS_SELECTOR: [By.CSS_SELECTOR.casefold(),
                              By.CSS_SELECTOR.replace("_", " ").casefold(),
                              By.CSS_SELECTOR.replace(" ", "_").casefold(),
                              "css".casefold()],
        }

        if "=" in self.locator or ":" in self.locator:
            possible_by = self.locator.split("=")[0].split(":")[0]

            for key, value in bys.items():
                if possible_by.casefold() in value:
                    by = key
                    selector = self.locator[len(possible_by) + 1:]
                    return selector, by
        # self.locator has no explicit by
        if self.locator == "." or self.locator.startswith("./") or self.locator.startswith("/"):
            return self.locator, By.XPATH
        else:
            return self.locator, By.CSS_SELECTOR

    @property
    def selector(self) -> str:
        return self.selector_by_tuple[0]

    @property
    def by(self) -> str:
        return self.selector_by_tuple[1]

    @property
    def real_class_name(self) -> str:
        module = self.__class__.__module__
        name = self.__class__.__name__
        return f"{module}.{name}"

    ########
    # Print
    ########
    def __repr__(self):
        return self.full_name

    ##############
    # Validations
    ##############
    def _post_attach(self, parent: WebNode) -> None:
        super(WebNode, self)._post_attach(parent)
        self.validate()
        self.validate_unique_descendant_names()
        parent.nearest_named_ancestor_or_self().validate_unique_descendant_names()

    def validate(self) -> None:
        if self.name is not None:
            assert len(self.name) > 0, f"WebNode validation error: name={self.name}"

            try:
                int(self.name)
            except ValueError:
                pass
            else:
                assert False, f"WebNode validation error: name={self.name}. Name can not be an int"

            assert "__" not in self.name, f"WebNode validation error: name={self.name}. Name can not contain '__'"

        if self.locator is not None:
            assert len(self.locator) > 0, f"WebNode validation error: locator={self.locator}"

        if self.ignore_case_in_text_pattern is True:
            assert self.text_pattern is not None, \
                f"WebNode validation error: ignore_case_in_text_pattern={self.ignore_case_in_text_pattern}, " \
                f"text_pattern={self.text_pattern}"

        if self.use_regexp_in_text_pattern is True:
            assert self.text_pattern is not None, \
                f"WebNode validation error: use_regexp_in_text={self.use_regexp_in_text_pattern}, " \
                f"text_pattern={self.text_pattern}"

        if self.override_parent_selector is not None:
            assert len(self.override_parent_selector) > 0, \
                f"WebNode validation error: override_parent_selector={self.override_parent_selector}"

        if self.should_be_present is False:
            assert self.should_be_visible is False, \
                f"WebNode validation error: should_be_present={self.should_be_present}, " \
                f"should_be_visible={self.should_be_visible}"

        if self.should_be_visible is True:
            assert self.should_be_present is True, \
                f"WebNode validation error: should_be_visible={self.should_be_visible}, " \
                f"should_be_present={self.should_be_present}"

        if self.is_multiple is True:
            assert self.order is None, \
                f"WebNode validation error: is_multiple={self.is_multiple}, order={self.order}"
            assert self.name is not None, \
                f"WebNode validation error: is_multiple={self.is_multiple}, name={self.name}"

        if self.is_multiple_instance_from is not None:
            assert self.order is not None, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, order={self.order}"
            assert self.name == f"{self.is_multiple_instance_from.name}_{self.order}", \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, name={self.name}"
            assert self.locator == self.is_multiple_instance_from.locator, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, locator={self.locator}"
            assert self.text_pattern == self.is_multiple_instance_from.text_pattern, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, locator={self.text_pattern}"
            assert self.ignore_case_in_text_pattern == self.is_multiple_instance_from.ignore_case_in_text_pattern, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, " \
                f"ignore_case_in_text_pattern={self.ignore_case_in_text_pattern}"
            assert self.use_regexp_in_text_pattern == self.is_multiple_instance_from.use_regexp_in_text_pattern, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, " \
                f"use_regexp_in_text_pattern={self.use_regexp_in_text_pattern}"
            assert self.override_parent_selector == self.is_multiple_instance_from.override_parent_selector, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, " \
                f"override_parent_selector={self.override_parent_selector}"
            assert self.should_be_present == self.is_multiple_instance_from.should_be_present, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, " \
                f"should_be_present={self.should_be_present}"
            assert self.should_be_visible == self.is_multiple_instance_from.should_be_visible, \
                f"WebNode validation error: " \
                f"is_multiple_instance_from={self.is_multiple_instance_from}, " \
                f"should_be_visible={self.should_be_visible}"

        if self.is_template is True:
            assert self.name is not None, \
                f"WebNode validation error: is_template={self.is_template}, name={self.name}"
            assert len(self.template_args) > 0 or len(self.template_kwargs) > 0, \
                f"WebNode validation error: is_template={self.is_template}, " \
                f"template_args={self.template_args}, template_kwargs={self.template_kwargs}"

        if len(self.template_args) > 0:
            assert self.template is not None, \
                f"WebNode validation error: template_args={self.template_args}, template={self.template}"

        if len(self.template_kwargs) > 0:
            assert self.template is not None, \
                f"WebNode validation error: template_kwargs={self.template_kwargs}, template={self.template}"

    def validate_unique_descendant_names(self) -> None:
        nearest = self.nearest_named_ancestor_or_self()
        named: typing.List[WebNode] = anytree.findall(nearest, lambda node: node.name is not None)
        if nearest in named:
            named.remove(nearest)
        named = [node for node in named if node.nearest_named_ancestor_or_self() == nearest]
        for node in named:
            found = nearest._find_directly_descendant_nodes_with_name(node.name)
            assert len(found) == 1, f"Found {len(found)} nodes with name '{node.name}' starting from node: {nearest}"
            assert found[0] == node, \
                f"Found one node with name '{node.name}', but it is not the expected node. \n" \
                f"Real: {found[0]} \nExpected: {node}"

    ############
    # Init node
    ############
    def init_node(self) -> None:
        pass

    ################
    # Finding nodes
    ################
    def nearest_named_ancestor_or_self(self) -> WebNode:
        if self.is_root or self.name is not None:
            return self
        else:
            return self.parent.nearest_named_ancestor_or_self()

    def _find_directly_descendant_nodes_with_name(self, name: str) -> typing.List[WebNode]:
        named = self.nearest_named_ancestor_or_self()
        nodes: typing.List[WebNode] = anytree.findall_by_attr(self, name)
        return [node for node in nodes if node.parent.nearest_named_ancestor_or_self() == named and node != self]

    def _find_descendant_nodes(self, path: str) -> typing.List[WebNode]:
        names = path.split(self.separator)
        while "" in names:
            names.remove("")
        assert len(names) > 0, f"Invalid path: {path}"
        nodes: typing.List[WebNode] = anytree.findall_by_attr(self, names[0])
        if self in nodes:
            nodes.remove(self)
        for name in names[1:]:
            new_nodes = []
            for pre_node in nodes:
                new_nodes = new_nodes + anytree.findall_by_attr(pre_node, name)
            nodes = new_nodes
        return nodes

    def get_node(self, path: str, only_descendants: bool = True) -> WebNode:
        base_node = self
        found = base_node._find_descendant_nodes(path)
        assert len(found) <= 1, f"Found {len(found)} nodes with path '{path}' starting from node: {base_node}"
        if len(found) == 1:
            return found[0]
        else:
            assert only_descendants is False and self.is_root is False, \
                f"Node with path '{path}' (only_descendants={only_descendants}) not found starting from node: {self}"
            while base_node.parent is not None:
                base_node_parent: WebNode = base_node.parent
                base_node = base_node_parent.nearest_named_ancestor_or_self()
                found = base_node._find_descendant_nodes(path)
                assert len(found) <= 1, f"Found {len(found)} nodes with path '{path}' starting from node: {base_node}"
                if len(found) == 1:
                    return found[0]
            else:
                assert False, \
                    f"Node with path '{path}' (only_descendants={only_descendants}, whole tree has been searched) " \
                    f"not found starting from node: {self}"

    #######################
    # Finding web_elements
    #######################
    def web_elements(self, only_visible: bool = False) -> typing.List[WebElement]:
        elements = self.pom_base_case.find_elements(self.root.selector, self.root.by)
        if elements is None:
            elements = []
        # validate elements
        elements: typing.List[WebElement] = [
            element for element in elements
            if util.Util.web_element_match_text_pattern(element,
                                                        self.root.text_pattern,
                                                        self.root.use_regexp_in_text_pattern,
                                                        self.root.ignore_case_in_text_pattern)
        ]
        if self.root.order is not None:
            one_element: WebElement = elements[self.root.order]
            elements = [one_element]

        for node in self.path[1:]:
            new_elements = []
            for element in elements:
                new_candidates = element.find_elements(by=node.by, value=node.selector)
                if new_candidates is None:
                    new_candidates = []
                # validate new_candidates
                new_candidates: typing.List[WebElement] = [
                    element for element in new_candidates
                    if util.Util.web_element_match_text_pattern(element,
                                                                node.text_pattern,
                                                                node.use_regexp_in_text_pattern,
                                                                node.ignore_case_in_text_pattern)
                ]
                if node.order is not None:
                    one_element: WebElement = new_candidates[node.order]
                    new_candidates = [one_element]
                new_elements = new_elements + new_candidates
            elements = new_elements
        if only_visible is True:
            elements = [element for element in elements if element.is_displayed() is True]
        elements = [util.Util.attach_canonical_xpath_css_and_node_to_web_element(element, self.pom_base_case.driver)
                    for element in elements]
        if None in elements:
            # Restart process
            return self.web_elements(only_visible)
        return elements

    def web_element(self, prefer_visible: bool = True) -> typing.Optional[WebElement]:
        if prefer_visible is True:
            visible_elements = self.web_elements(only_visible=True)
            if len(visible_elements) > 0:
                return visible_elements[0]
        elements = self.web_elements()
        if len(elements) == 0:
            return None
        else:
            return self.web_elements()[0]

    ##############
    # Node status
    ##############
    def is_present(self) -> bool:
        if self.web_element() is None:
            return False
        else:
            return True

    def is_visible(self) -> bool:
        if len(self.web_elements(only_visible=True)) == 0:
            return False
        else:
            return True

    #######
    # Wait
    #######
    def wait_until_present(self,
                           timeout: typing.Union[int, float] = None,
                           raise_error: bool = True) -> typing.Optional[WebElement]:
        self.pom_base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.pom_base_case, settings.LARGE_TIMEOUT)
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (timeout * 1000.0)
        for x in range(int(timeout * 10)):
            s_utils.check_if_time_limit_exceeded()
            element = self.web_element()
            if element is not None:
                return element
            else:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        if raise_error is True:
            plural = "s"
            if timeout == 1 or timeout == 1.0:
                plural = ""
            message = f"WebNode was not present after {timeout} second{plural}: {self}"
            timeout_exception(NoSuchElementException, message)
        else:
            return None

    def wait_until_not_present(self,
                               timeout: typing.Union[int, float] = None,
                               raise_error: bool = True) -> bool:
        self.pom_base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.pom_base_case, settings.LARGE_TIMEOUT)
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (timeout * 1000.0)
        for x in range(int(timeout * 10)):
            s_utils.check_if_time_limit_exceeded()
            if self.web_element() is None:
                return True
            else:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        if raise_error is True:
            plural = "s"
            if timeout == 1 or timeout == 1.0:
                plural = ""
            message = f"WebNode was still present after {timeout} second{plural}: {self}"
            timeout_exception(Exception, message)
        else:
            return False

    def wait_until_visible(self,
                           timeout: typing.Union[int, float] = None,
                           raise_error: bool = True) -> typing.Optional[WebElement]:
        self.pom_base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.pom_base_case, settings.LARGE_TIMEOUT)
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (timeout * 1000.0)
        element = None
        for x in range(int(timeout * 10)):
            s_utils.check_if_time_limit_exceeded()
            element = self.web_element()
            if element is not None and element.is_displayed() is True:
                return element
            else:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        if raise_error is True:
            plural = "s"
            if timeout == 1 or timeout == 1.0:
                plural = ""
            if element is None:
                message = f"WebNode was not present after {timeout} second{plural}: {self}"
                timeout_exception(NoSuchElementException, message)
            else:
                # element is not visible
                message = f"WebNode was not visible after {timeout} second{plural}: {self}"
                timeout_exception(ElementNotVisibleException, message)
        else:
            return None

    def wait_until_not_visible(self,
                               timeout: typing.Union[int, float] = None,
                               raise_error: bool = True) -> bool:
        self.pom_base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.pom_base_case, settings.LARGE_TIMEOUT)
        start_ms = time.time() * 1000.0
        stop_ms = start_ms + (timeout * 1000.0)
        for x in range(int(timeout * 10)):
            s_utils.check_if_time_limit_exceeded()
            element = self.web_element()
            if element is None or element.is_displayed() is False:
                return True
            else:
                now_ms = time.time() * 1000.0
                if now_ms >= stop_ms:
                    break
                time.sleep(0.1)
        if raise_error is True:
            plural = "s"
            if timeout == 1 or timeout == 1.0:
                plural = ""
            message = f"WebNode was still visible after {timeout} second{plural}: {self}"
            timeout_exception(Exception, message)
        else:
            return False

    def wait_until_loaded(self,
                          timeout: typing.Union[int, float] = None,
                          raise_error: bool = True,
                          force_wait_until_present: bool = True,
                          force_wait_until_visible: bool = True) -> bool:
        if self.should_be_present is True or force_wait_until_present is True:
            present = self.wait_until_present(timeout, raise_error)
            if present is None:
                return False
        if self.should_be_visible is True or force_wait_until_visible is True:
            visible = self.wait_until_visible(timeout, raise_error)
            if visible is None:
                return False
        for child in self.children:
            child: WebNode
            if child.is_template is True:
                continue
            loaded = child.wait_until_loaded(timeout,
                                             raise_error,
                                             force_wait_until_present=False,
                                             force_wait_until_visible=False)
            if loaded is False:
                return False
        return True

    ###############
    # Copy WebNode
    ###############
    def copy(self, recursive: bool = False) -> WebNode:
        node = self.__class__(**self.relevant_properties)
        if recursive is True:
            for child in self.children:
                child: WebNode
                child_copy = child.copy(recursive=True)
                child_copy.parent = node
        return node

    ####################
    # Multiple children
    ####################
    def get_multiple_instances(self) -> typing.List[WebNode]:
        assert self.is_multiple is True, f"get_multiple_children only works if is_multiple is True. Node: {self}"

        # Clean previous multiple_instances
        parent: WebNode = self.parent
        for child in parent.children[:]:
            child: WebNode
            if child.is_multiple_instance_from == self:
                child.parent = None

        # Calculate multiple_instances
        number = len(self.web_elements())
        nodes = []
        for n in range(number):
            node = self.copy(recursive=True)
            node.name = f"{self.name}_{n}"
            node.order = n
            node.is_multiple = False
            node.is_multiple_instance_from = self.name
            node.parent = self.parent
            nodes.append(node)
        return nodes

    ##########
    # Replace
    ##########
    def replace(self,
                new_node: WebNode,
                keep_new_children: bool = True,
                keep_replaced_children: bool = False) -> WebNode:
        parent: WebNode = self.parent
        self.parent = None
        new_node.parent = parent
        if keep_new_children is False:
            for child in new_node.children[:]:
                child: WebNode
                child.parent = None
        if keep_replaced_children is True:
            for child in self.children[:]:
                child: WebNode
                child.parent = new_node
        return new_node

    def replace_with_desired_class_node(self, recursive: bool = True) -> WebNode:
        if self.desired_class_name is not None and self.real_class_name != self.desired_class_name:
            new_class_parts = self.desired_class_name.split(".")
            assert len(new_class_parts) > 1, f"Invalid desired_class_name={self.desired_class_name}. Node: {self}"
            new_module_name = ".".join(new_class_parts[:-1])
            new_module = importlib.import_module(new_module_name)
            new_class = getattr(new_module, new_class_parts[-1])
            new_node: WebNode = new_class(**self.relevant_properties)
            new_node.desired_class_name = None
            new_node = self.replace(new_node, keep_new_children=False, keep_replaced_children=True)
        else:
            new_node = self
        if recursive is True:
            for child in new_node.children[:]:
                child: WebNode
                child.replace_with_desired_class_node(recursive=True)
        return new_node

    ######################
    # Load node from file
    ######################
    @classmethod
    def load_node_from_file(cls, file: os.PathLike = None) -> typing.Optional[WebNode]:
        if file is None:
            file = inspect.getfile(cls)
        return file_loader.FileLoader.load_node_from_file(file)

    #######################
    # SeleniumBase actions
    #######################
    def click(self, timeout: typing.Union[int, float] = None, delay: int = 0) -> None:
        return self.pom_base_case.click(self, timeout=timeout, delay=delay)

    def slow_click(self, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.slow_click(self, timeout=timeout)

    def double_click(self, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.double_click(self, timeout=timeout)

    def click_chain(self, timeout: typing.Union[int, float] = None, spacing: int = 0) -> None:
        return self.pom_base_case.click_chain(self, timeout=timeout, spacing=spacing)

    def type(self, text: str, timeout: typing.Union[int, float] = None, retry: bool = True) -> None:
        return self.pom_base_case.type(self, text, timeout=timeout, retry=retry)

    def add_text(self, text, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.add_text(self, text, timeout=timeout)

    def submit(self) -> None:
        return self.pom_base_case.submit(self)

    def clear(self, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.clear(self, timeout=timeout)

    def is_text_visible(self, text: str) -> bool:
        return self.pom_base_case.is_text_visible(text, self)

    def get_text(self, timeout: typing.Union[int, float] = None) -> str:
        return self.pom_base_case.get_text(self, timeout=timeout)

    def get_attribute(self,
                      attribute: str,
                      timeout: typing.Union[int, float] = None,
                      hard_fail: bool = True) -> typing.Any:
        return self.pom_base_case.get_attribute(self, attribute, timeout=timeout, hard_fail=hard_fail)

    def set_attribute(self, attribute: str, value: typing.Any, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.set_attribute(self, attribute, value, timeout=timeout)

    def set_attributes(self, attribute: str, value: typing.Any) -> None:
        return self.pom_base_case.set_attributes(self, attribute, value)

    def remove_attribute(self, attribute: str, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.remove_attribute(self, attribute, timeout=timeout)

    def remove_attributes(self, attribute: str) -> None:
        return self.pom_base_case.remove_attributes(self, attribute)

    def get_property_value(self, property: str, timeout: typing.Union[int, float] = None) -> typing.Any:
        return self.pom_base_case.get_property_value(self, property, timeout=timeout)

    def get_image_url(self, timeout: typing.Union[int, float] = None) -> str:
        return self.pom_base_case.get_image_url(self, timeout=timeout)

    def click_visible_elements(self, limit: int = 0, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.click_visible_elements(self, limit=limit, timeout=timeout)

    def click_nth_visible_element(self, number: int, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.click_nth_visible_element(self, number, timeout=timeout)

    def click_if_visible(self) -> None:
        return self.pom_base_case.click_if_visible(self)

    def is_selected(self, timeout: typing.Union[int, float] = None) -> bool:
        return self.pom_base_case.is_selected(self, timeout=timeout)

    def select_if_unselected(self) -> None:
        return self.pom_base_case.select_if_unselected(self)

    def unselect_if_selected(self) -> None:
        return self.pom_base_case.unselect_if_selected(self)

    def is_element_in_an_iframe(self) -> bool:
        return self.pom_base_case.is_element_in_an_iframe(self)

    def switch_to_frame_of_element(self) -> typing.Optional[str]:
        return self.pom_base_case.switch_to_frame_of_element(self)

    def hover_on_element(self) -> None:
        return self.pom_base_case.hover_on_element(self)

    def hover_and_click(self, click_node: typing.Union[str, WebNode], timeout: typing.Union[int, float] = None) -> None:
        if isinstance(click_node, str):
            click_node = self.get_node(click_node, only_descendants=False)
        return self.pom_base_case.hover_and_click(self, click_node, timeout=timeout)

    def hover_and_double_click(self,
                               click_node: typing.Union[str, WebNode],
                               timeout: typing.Union[int, float] = None) -> None:
        if isinstance(click_node, str):
            click_node = self.get_node(click_node, only_descendants=False)
        return self.pom_base_case.hover_and_double_click(self, click_node, timeout=timeout)

    def drag_and_drop(self,
                      drop_node: typing.Union[str, WebNode],
                      timeout: typing.Union[int, float] = None) -> None:
        if isinstance(drop_node, str):
            drop_node = self.get_node(drop_node, only_descendants=False)
        return self.pom_base_case.drag_and_drop(self, drop_node, timeout=timeout)

    def select_option_by_text(self, option: str, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.select_option_by_text(self, option, timeout=timeout)

    def select_option_by_index(self, option: int, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.select_option_by_index(self, option, timeout=timeout)

    def select_option_by_value(self, option: str, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.select_option_by_value(self, option, timeout=timeout)

    def bring_to_front(self) -> None:
        return self.pom_base_case.bring_to_front(self)

    def highlight_click(self, loops: int = 3, scroll: bool = True) -> None:
        return self.pom_base_case.highlight_click(self, loops=loops, scroll=scroll)

    def highlight_update_text(self, text: str, loops: int = 3, scroll: bool = True) -> None:
        return self.pom_base_case.highlight_update_text(self, text, loops=loops, scroll=scroll)

    def highlight(self, loops: int = 4, scroll: bool = True) -> None:
        return self.pom_base_case.highlight(self, loops=loops, scroll=scroll)

    def press_up_arrow(self, times: int = 1) -> None:
        return self.pom_base_case.press_up_arrow(self, times=times)

    def press_down_arrow(self, times: int = 1) -> None:
        return self.pom_base_case.press_down_arrow(self, times=times)

    def press_left_arrow(self, times: int = 1) -> None:
        return self.pom_base_case.press_left_arrow(self, times=times)

    def press_right_arrow(self, times: int = 1) -> None:
        return self.pom_base_case.press_right_arrow(self, times=times)

    def scroll_to(self) -> None:
        return self.pom_base_case.scroll_to(self)

    def slow_scroll_to(self) -> None:
        return self.pom_base_case.slow_scroll_to(self)

    def js_click(self, all_matches: bool = False) -> None:
        return self.pom_base_case.js_click(self, all_matches=all_matches)

    def js_click_all(self) -> None:
        return self.pom_base_case.js_click_all(self)

    def jquery_click(self) -> None:
        return self.pom_base_case.jquery_click(self)

    def jquery_click_all(self) -> None:
        return self.pom_base_case.jquery_click_all(self)

    def hide_element(self) -> None:
        return self.pom_base_case.hide_element(self)

    def hide_elements(self) -> None:
        return self.pom_base_case.hide_elements(self)

    def show_element(self) -> None:
        return self.pom_base_case.show_element(self)

    def show_elements(self) -> None:
        return self.pom_base_case.show_elements(self)

    def remove_element(self) -> None:
        return self.pom_base_case.remove_element(self)

    def remove_elements(self) -> None:
        return self.pom_base_case.remove_elements(self)

    def choose_file(self, file_path: os.PathLike, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.choose_file(self, file_path, timeout=timeout)

    def save_element_as_image_file(self, file_name: os.PathLike, folder: os.PathLike = None) -> None:
        return self.pom_base_case.save_element_as_image_file(self, file_name, folder)

    def set_value(self, text: str, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.set_value(self, text, timeout=timeout)

    def js_update_text(self, text: str, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.js_update_text(self, text, timeout=timeout)

    def jquery_update_text(self, text: str, timeout: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.jquery_update_text(self, text, timeout=timeout)

    def add_tour_step(self,
                      message: str,
                      name: str = None,
                      title: str = None,
                      theme: str = None,
                      alignment: str = None,
                      duration: typing.Union[int, float] = None) -> None:
        return self.pom_base_case.add_tour_step(message, self, name, title, theme, alignment, duration)

    def post_message_and_highlight(self, message) -> None:
        return self.pom_base_case.post_message_and_highlight(message, self)

    def find_text(self, text: str, timeout: typing.Union[int, float] = None) -> WebElement:
        return self.pom_base_case.find_text(text, self, timeout=timeout)

    def wait_for_exact_text_visible(self, text: str, timeout: typing.Union[int, float] = None) -> WebElement:
        return self.pom_base_case.wait_for_exact_text_visible(text, self, timeout=timeout)

    def assert_text(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.pom_base_case.assert_text(text, self, timeout=timeout)

    def assert_exact_text(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.pom_base_case.assert_exact_text(text, self, timeout=timeout)

    def wait_for_text_not_visible(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.pom_base_case.wait_for_text_not_visible(text, self, timeout=timeout)

    def assert_text_not_visible(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.pom_base_case.assert_text_not_visible(text, self, timeout=timeout)
