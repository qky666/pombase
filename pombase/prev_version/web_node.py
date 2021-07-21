from __future__ import annotations

import typing
import anytree
import collections
import itertools
import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from seleniumbase.config import settings
from seleniumbase import BaseCase

from cssselect.xpath import GenericTranslator

import pombase.util
from pombase import util
from pombase.prev_version import action, base_settings

SelectorByTuple = collections.namedtuple("SelectorByTuple", "selector by")


class WebNode(anytree.node.anynode.AnyNode):
    separator = "__"
    duplicates_sep = f"{separator}_"
    id_prefix = "id_"
    by_selector_sep = (":", "=")
    bys: typing.Dict[str, typing.List[str]] = {
        By.ID: [By.ID, "id"],
        By.XPATH: [By.XPATH, "xpath"],
        By.LINK_TEXT: [By.LINK_TEXT, "link", "link_text"],
        By.PARTIAL_LINK_TEXT: [By.PARTIAL_LINK_TEXT, "partial_link", "partial_link_text"],
        By.NAME: [By.NAME, "name"],
        By.TAG_NAME: [By.TAG_NAME, "tag", "tag_name"],
        By.CLASS_NAME: [By.CLASS_NAME, "class", "class_name"],
        By.CSS_SELECTOR: [By.CSS_SELECTOR, "css", "css_selector"],
    }

    # CSS translator
    translator = GenericTranslator()

    # util
    By = By
    Keys = Keys

    def __init__(self,
                 locator: str = None,  # Allow "id=my_selector", "id:my_selector", etc.
                 *,
                 parent: WebNode = None,
                 children: typing.Iterable[WebNode] = None,
                 name: str = None,
                 order: int = None,
                 override_parent_locator: typing.Union[str, bool, WebNode] = None,
                 valid_count: typing.Union[int,
                                           range,
                                           itertools.count,
                                           typing.List[int]] = range(2),
                 ignore_invisible: bool = True,
                 value_timeout: typing.Union[int, float] = None,
                 base_case: BaseCase = None,
                 **kwargs,
                 ):
        if children is None:
            children = []

        # Very special case
        if locator == ".":
            locator = None

        if override_parent_locator is True:
            override_parent_locator = "html"
        elif override_parent_locator is False:
            override_parent_locator = None
        elif isinstance(override_parent_locator, WebNode):
            override_parent_locator = override_parent_locator.selector

        if override_parent_locator is not None and locator is None:
            locator = override_parent_locator
            override_parent_locator = None

        if valid_count is None:
            if order is None:
                valid_count = itertools.count()
            else:
                valid_count = [0, 1]
        if isinstance(valid_count, int):
            valid_count = [valid_count, ]

        if value_timeout is None:
            value_timeout = settings.MINI_TIMEOUT

        if value_timeout < 0:
            value_timeout = 0

        super().__init__(
            locator=locator,
            # Delay this so validate() is called at the end
            # parent=parent,
            # children=children,
            name=name,
            order=order,
            override_parent_locator=override_parent_locator,
            valid_count=valid_count,
            ignore_invisible=ignore_invisible,
            value_timeout=value_timeout,
            _base_case=base_case,
            _kwargs=kwargs,
            **kwargs,
        )

        # This is redundant, but we want to help PyCharm
        self.locator = locator
        # self.parent: WebNode = parent
        # self.children: typing.Iterable[WebNode] = children
        self.name = name
        self.order = order
        self.override_parent_locator: typing.Optional[str] = override_parent_locator
        self.valid_count = valid_count
        self.ignore_invisible = ignore_invisible,
        self.value_timeout = value_timeout
        self._base_case = base_case
        self._kwargs = kwargs
        # for key, value in kwargs.items():
        #     setattr(self, key, value)

        # Used for auto-generated nodes (multiple nodes)
        self.volatile: bool = False
        self._multiple_web_nodes_cache = []

        # Util
        self.logger = logging.getLogger()

        # Init node
        self.init_node()

        # Validation -> In _post_attach
        # self.validate()
        self.parent: WebNode = parent
        self.children: typing.Iterable[WebNode] = children

    ############
    # Accessors
    ############
    # pom_base_case
    @property
    def base_case(self) -> typing.Optional[BaseCase]:
        if self._base_case is None:
            if self.is_root:
                return None
            else:
                self.parent: WebNode
                return self.parent.base_case
        else:
            return self._base_case

    @base_case.setter
    def base_case(self, value: typing.Optional[BaseCase]) -> None:
        self._base_case = value

    ######################
    # Computed properties
    ######################
    @property
    def max_count(self) -> typing.Optional[int]:
        if type(self.valid_count) == itertools.count:
            return None
        else:
            return max(self.valid_count)

    @property
    def multiple(self) -> bool:
        if self.max_count is None or self.max_count > 1:
            return True
        else:
            return False

    @property
    def relevant_properties(self) -> typing.Dict[str]:
        return dict(
            locator=self.locator,
            name=self.name,
            order=self.order,
            override_parent_locator=self.override_parent_locator,
            valid_count=self.valid_count,
            ignore_invisible=self.ignore_invisible,
            value_timeout=self.value_timeout,
            base_case=self._base_case,
            **self._kwargs,
        )

    @property
    def _node_id(self) -> str:
        return f"{self.id_prefix}{id(self)}"

    @property
    def full_name(self) -> str:
        return self._full_name_from_ancestor()

    @classmethod
    def selector_by_tuple_for_locator(cls, locator: str) -> SelectorByTuple:
        bys = {key: pombase.util.expand_replacing_spaces_and_underscores(value) for key, value in cls.bys.items()}

        possible_by = locator
        used_sep = None
        for sep in cls.by_selector_sep:
            if sep in possible_by:
                possible_by = possible_by.split(sep)[0]
                used_sep = sep

        if used_sep is not None:
            for key, value in bys.items():
                if pombase.util.caseless_text_in_texts(possible_by, value):
                    by = key
                    selector = locator[len(possible_by) + len(used_sep):]
                    return SelectorByTuple(selector, by)

        # self.locator has no explicit by
        if locator == "." \
                or locator.startswith("./") \
                or locator.startswith("/") \
                or locator.startswith("("):
            return SelectorByTuple(locator, By.XPATH)
        else:
            return SelectorByTuple(locator, By.CSS_SELECTOR)

    @classmethod
    def locator_to_css(cls, locator: str) -> typing.Optional[str]:
        selector, by = cls.selector_by_tuple_for_locator(locator)
        if by == cls.By.ID:
            return f"#{selector}"
        elif by == cls.By.XPATH:
            return None
        elif by == cls.By.LINK_TEXT:
            return None
        elif by == cls.By.PARTIAL_LINK_TEXT:
            return None
        elif by == cls.By.NAME:
            return f"[name='{selector}']"
        elif by == cls.By.TAG_NAME:
            return selector
        elif by == cls.By.CLASS_NAME:
            return f".{selector}"
        elif by == cls.By.CSS_SELECTOR:
            return selector
        else:
            assert False, f"Unknown 'by': {by}. Locator: {locator}"

    @classmethod
    def locator_to_xpath(cls, locator: str) -> str:
        selector, by = cls.selector_by_tuple_for_locator(locator)
        if by == cls.By.ID:
            return f".//*[@id='{selector}']"
        elif by == cls.By.XPATH:
            return selector
        elif by == cls.By.LINK_TEXT:
            return f".//a[normalize-space(.)='{selector}']"
        elif by == cls.By.PARTIAL_LINK_TEXT:
            return f".//a[contains(normalize-space(.),'{selector}')]"
        elif by == cls.By.NAME:
            return f".//*[@name='{selector}']"
        elif by == cls.By.TAG_NAME:
            return f".//{selector}"
        elif by == cls.By.CLASS_NAME:
            return f".//*[contains(concat(' ',normalize-space(@class),' '),' {selector} ')]"
        elif by == cls.By.CSS_SELECTOR:
            return cls.translator.css_to_xpath(selector, ".//")
        else:
            assert False, f"Unknown 'by': {by}. Locator: {locator}"

    @property
    def _node_selector_by_tuple(self) -> SelectorByTuple:
        return self.selector_by_tuple_for_locator(self.locator)

    @property
    def _node_selector(self) -> typing.Optional[str]:
        return self._node_selector_by_tuple.selector

    @property
    def _node_by(self) -> typing.Optional[str]:
        return self._node_selector_by_tuple.by

    @property
    def _full_locator(self) -> str:
        path_with_locator_or_order: typing.List[WebNode] = \
            [node for node in self.path if node.locator is not None or node.order is not None]

        if len(path_with_locator_or_order) == 0:
            return f"{self.By.CSS_SELECTOR}{self.by_selector_sep[0]}html"

        path_with_override = [node for node in path_with_locator_or_order if node.override_parent_locator is not None]
        last_with_override = path_with_override[-1] if len(path_with_override) > 0 else None

        if last_with_override is not None:
            last_with_override_index = path_with_override.index(last_with_override)
            selector, by = self.selector_by_tuple_for_locator(last_with_override.override_parent_locator)
            path_with_locator_or_order = path_with_locator_or_order[last_with_override_index:]
        else:
            selector = ""
            by = self.By.CSS_SELECTOR

        if by == self.By.CSS_SELECTOR:
            css = selector
            for node in path_with_locator_or_order:
                node_css = self.locator_to_css(node.locator) if node.locator is not None else ""
                if node_css is None or node.order is not None:
                    break
                css = f"{css} {node_css}".strip()
            else:
                return f"{by}{self.by_selector_sep[0]}{css}"

        xpath = selector
        for node in path_with_locator_or_order:
            xpath_no_order = self.locator_to_xpath(node.locator) if node.locator is not None else "."
            if xpath_no_order.startswith(("/", "(")):
                # Reset xpath, start from document root
                xpath = xpath_no_order
            else:
                # xpath_no_order is "." or starts with "./". Remove "." so we can concatenate
                assert xpath_no_order == "." or xpath_no_order.startswith("./"), \
                    f"xpath_no_order should start with './', but it is: {xpath_no_order}"
                xpath_no_order = xpath_no_order[1:]
                xpath = f"{xpath}{xpath_no_order}"
            if node.order is not None:
                xpath = f"({xpath})[{node.order}]"
        return f"{self.By.XPATH}{self.by_selector_sep[0]}{xpath}"

    @property
    def _full_selector_by_tuple(self) -> SelectorByTuple:
        return self.selector_by_tuple_for_locator(self._full_locator)

    @property
    def selector(self) -> str:
        return self._full_selector_by_tuple.selector

    @property
    def by(self) -> str:
        return self._full_selector_by_tuple.by

    ########
    # Print
    ########
    def __repr__(self):
        return self.full_name

    ################
    # Set attribute
    ################
    # def __setattr__(self, name: str, value:typing.Any) -> None:
    #     super().__setattr__(name, value)
    #     if isinstance(value, WebNode) and name != "parent" and name.startswith("_") is False:
    #         if value.name is None:
    #             value.name = name
    #         assert name == value.name, \
    #             f"Attribute name is '{name}', node name is '{value.name}'. Should be equal. Node: {self}"
    #         value.parent = self

    ##############
    # Validations
    ##############
    def _post_attach(self, parent: WebNode) -> None:
        super()._post_attach(parent)
        self.validate()
        parent.validate()
        self.validate_unique_descendant_names()
        parent.find_nearest_named().validate_unique_descendant_names()

    def validate(self) -> None:
        if self.name is None:
            if self.order is not None:
                assert len(self.valid_count) == 1, \
                    f"WebNode validation error: name={self.name}, order={self.order}, " \
                    f"valid_count={self.valid_count}"
                for valid in self.valid_count:
                    assert valid in [0, 1], \
                        f"WebNode validation error: name={self.name}, order={self.order}, " \
                        f"valid_count={self.valid_count}"
            elif type(self.valid_count) == itertools.count:
                assert 0 in self.valid_count is False, \
                    f"WebNode validation error: name={self.name}, order={self.order}, " \
                    f"valid_count={self.valid_count}"

        if self.name is not None:
            assert len(self.name) > 0, f"WebNode validation error: name={self.name}. Name length should not be 0"
            assert self.separator not in self.name, \
                f"WebNode validation error: name={self.name}. Name should not include '{self.separator}'"

            if self.volatile is False:
                try:
                    int(self.name)
                except ValueError:
                    pass
                else:
                    assert False, \
                        f"WebNode validation error: name={self.name}, volatile={self.volatile}. Name can not be an int"

            assert self.separator not in self.name, \
                f"WebNode validation error: name={self.name}. Name should not include '{self.separator}'"

            assert self.name.startswith("_") is False, \
                f"WebNode validation error: name={self.name}. Name should start with '_'"

            assert self.name.endswith("_") is False, \
                f"WebNode validation error: name={self.name}. Name should end with '_'"

            assert self.name.isidentifier() is True, \
                f"WebNode validation error: name={self.name}. Name should be a valid identifier"

        if self.locator is not None:
            assert len(self.locator) > 0, \
                f"WebNode validation error: locator={self.locator}. Locator length should not be 0"

        if self.order is not None:
            for valid in self.valid_count:
                assert valid in [0, 1], \
                    f"WebNode validation error: order={self.order}, valid_count={self.valid_count}"

        if self.override_parent_locator is not None:
            assert len(self.override_parent_locator) > 0, \
                f"WebNode validation error: override_parent_locator={self.override_parent_locator}"

        for valid in self.valid_count:
            if valid not in [0, 1]:
                assert self.order is None, \
                    f"WebNode validation error: valid_count={self.valid_count}, order={self.order}"
                break

    def validate_unique_descendant_names(self) -> None:
        nearest = self.find_nearest_named()
        named: typing.List[WebNode] = list(anytree.findall(nearest, lambda node: node.name is not None))
        if nearest in named:
            named.remove(nearest)
        named = [node for node in named if node.parent.find_nearest_named() == nearest]
        for node in named:
            found = nearest._find_directly_descendant_nodes(node.name)
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
    def find_nearest_named(self) -> WebNode:
        if self.is_root or self.name is not None:
            return self
        else:
            return self.parent.find_nearest_named()

    def _find_directly_descendant_nodes(self, name: str) -> typing.List[WebNode]:
        nearest = self.find_nearest_named()
        nodes: typing.List[WebNode] = anytree.findall_by_attr(self, name)
        return [node for node in nodes if node.parent.find_nearest_named() == nearest and node != self]

    def _find_descendant_nodes(self, path: str) -> typing.List[WebNode]:
        names = path.split(self.separator)
        while "" in names:
            names.remove("")
        assert len(names) > 0, f"Invalid path: {path}"
        first_name = names[0]
        try:
            first_int = int(first_name)
            nodes = [self.multiple_web_node(first_int), ]
        except ValueError:
            nodes: typing.List[WebNode] = anytree.findall_by_attr(self, names[0])
        if self in nodes:
            nodes.remove(self)
        for name in names[1:]:
            new_nodes = []
            try:
                name_int = int(name)
                for pre_node in nodes:
                    new_node = pre_node.multiple_web_node(name_int)
                    if new_node is not None:
                        new_nodes.append(new_node)
            except ValueError:
                for pre_node in nodes:
                    new_nodes = new_nodes + anytree.findall_by_attr(pre_node, name)

            nodes = new_nodes
        return nodes

    def find_node(self, path: str, descendants_only: bool = True) -> WebNode:
        base_node = self
        found = base_node._find_descendant_nodes(path)
        assert len(found) <= 1, f"Found {len(found)} nodes with path '{path}' starting from node: {base_node}"
        if len(found) == 1:
            return found[0]
        else:
            assert descendants_only is False and self.is_root is False, \
                f"Node with path '{path}' (only_descendants={descendants_only}) not found starting from node: {self}"
            while base_node.parent is not None:
                base_node_parent: WebNode = base_node.parent
                base_node = base_node_parent.find_nearest_named()
                found = base_node._find_descendant_nodes(path)
                assert len(found) <= 1, f"Found {len(found)} nodes with path '{path}' starting from node: {base_node}"
                if len(found) == 1:
                    return found[0]
            else:
                assert False, \
                    f"Node with path '{path}' (only_descendants={descendants_only}, whole tree has been searched) " \
                    f"not found starting from node: {self}"

    ###########
    # Multiple
    ###########
    def __len__(self):
        elements = self.base_case.find_visible_elements(self.selector, self.by) if self.ignore_invisible \
            else self.base_case.find_elements(self.selector, self.by)
        len_elements = len(elements)
        if self.multiple is False:
            assert len_elements <= 1, f"Inconsistency: multiple='{self.multiple}', len={len_elements}. Node: {self}"
        return len_elements

    def multiple_web_nodes(self) -> typing.List[WebNode]:
        if self.multiple is False:
            return []
        else:
            return [self.multiple_web_node(i) for i in range(len(self))]

    def multiple_web_node(self, order: int) -> typing.Optional[WebNode]:
        if self.multiple is False:
            return None
        else:
            for i in range(len(self._multiple_web_nodes_cache), order):
                node = self.copy(recursive=True)
                node.name = str(i)
                node.locator = None
                node.order = i
                node.valid_count = [0, 1]
                node.volatile = True
                node.parent = self
                self._multiple_web_nodes_cache.append(node)
            return self._multiple_web_nodes_cache[order]

    def _reset_multiple_web_nodes_cache(self) -> None:
        nodes = self._multiple_web_nodes_cache
        self._multiple_web_nodes_cache = []
        # Remove nodes from tree if they are volatile
        for node in nodes:
            if node.volatile:
                node.parent = None

    # def __getitem__(self, item: typing.Union[int, slice, str]) -> WebNode:
    #     if isinstance(item, (int, slice, str)) is False:
    #         raise TypeError(f"item should be int, slice or str, but 'item' is: {item}. Node: {self}")
    #
    #     if isinstance(item, str):
    #         try:
    #             return self.find_node(item)
    #         except AssertionError:
    #             raise KeyError(f"Key '{item}' not found in node: {self}")
    #
    #     self_len = len(self)
    #     real_item = item + self_len if item < 0 else item
    #     if real_item >= self_len or real_item < 0:
    #         raise IndexError(f"len={self_len}. Index out of range: {item}. Node: {self}")
    #     if real_item == 0 and self.order is not None:
    #         return self
    #     else:
    #         node = self.copy(recursive=True)
    #         node.order = item
    #         return node

    def __iter__(self):
        yield from self.multiple_web_nodes()

    ##############
    # Node status
    ##############
    def _has_valid_count(self, force_valid_count_greater_than_zero: bool = False) -> bool:
        num_elements = len(self)
        if num_elements in self.valid_count and \
                ((force_valid_count_greater_than_zero is False) or (num_elements > 0)):
            return True
        else:
            return False

    def has_valid_count(self) -> bool:
        return self._has_valid_count()

    #########
    # Iframe
    #########
    def is_iframe(self) -> bool:
        element = self.base_case.find_element(self.selector, self.by)
        if element is None:
            return False
        tag_name = element.tag_name
        if isinstance(tag_name, str) and pombase.util.caseless_equal(tag_name, "iframe"):
            return True
        else:
            return False

    def switch_to_default_content(self):
        self.base_case.switch_to_default_content()

    #########
    # Status
    #########
    def is_present(self) -> bool:
        return self.base_case.is_element_present(self.selector, self.by)

    def is_visible(self) -> bool:
        return self.base_case.is_element_visible(self.selector, self.by)

    #######
    # Wait
    #######
    def wait_until_present(self,
                           timeout: typing.Union[int, float] = None,
                           raise_error: bool = True) -> bool:
        self.logger.debug(f"Starting wait_until_present for node: {self}")
        self.base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.base_case, settings.LARGE_TIMEOUT)

        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode was not present after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self.is_present, timeout=timeout, raise_error=raise_error)
        return success

    def wait_until_not_present(self,
                               timeout: typing.Union[int, float] = None,
                               raise_error: bool = True) -> bool:
        self.logger.debug(f"Starting wait_until_not_present for node: {self}")
        self.base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.base_case, settings.LARGE_TIMEOUT)

        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode was still present after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self.is_present,
                                     timeout=timeout,
                                     expected=False,
                                     raise_error=raise_error)
        return success

    def wait_until_visible(self,
                           timeout: typing.Union[int, float] = None,
                           raise_error: bool = True) -> bool:
        self.logger.debug(f"Starting wait_until_visible for node: {self}")
        self.base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.base_case, settings.LARGE_TIMEOUT)

        present = self.wait_until_present(timeout, raise_error)
        if present is False:
            return False

        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode was not visible after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self.is_visible,
                                     timeout=timeout,
                                     raise_error=raise_error)
        return success

    def wait_until_not_visible(self,
                               timeout: typing.Union[int, float] = None,
                               raise_error: bool = True) -> bool:
        self.logger.debug(f"Starting wait_until_not_visible for node: {self}")
        self.base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.base_case, settings.LARGE_TIMEOUT)

        not_present = self.wait_until_not_present(timeout, raise_error)
        if not_present is False:
            return False

        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode was still visible after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self.is_visible,
                                     timeout=timeout,
                                     expected=False,
                                     raise_error=raise_error)
        return success

    def wait_until_valid_count(self,
                               timeout: typing.Union[int, float] = None,
                               raise_error: bool = True,
                               force_valid_count_greater_than_zero: bool = True, ) -> bool:
        self.logger.debug(f"Starting wait_until_valid_count for node: {self}")
        self.base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.base_case, settings.LARGE_TIMEOUT)

        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode had not valid count after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self._has_valid_count,
                                     args=[force_valid_count_greater_than_zero, ],
                                     timeout=timeout,
                                     raise_error=raise_error)
        return success

    def wait_until_loaded(self,
                          timeout: typing.Union[int, float] = None,
                          raise_error: bool = True,
                          force_valid_count_greater_than_zero: bool = True, ) -> bool:
        self.logger.debug(f"Starting wait_until_loaded for node: {self}")
        # Handle frames
        element_in_iframe = self.base_case.is_element_in_an_iframe(self.selector, self.by)
        if element_in_iframe:
            for node in self.path[:-1]:
                node: WebNode
                if node.is_iframe() is True:
                    node.switch_to_frame(timeout)

        valid_count = self.wait_until_valid_count(timeout,
                                                  raise_error,
                                                  force_valid_count_greater_than_zero)
        if valid_count is False:
            if element_in_iframe is True:
                self.switch_to_default_content()
            return False

        node_list: typing.List[WebNode]
        if self.multiple:
            node_list = self.multiple_web_nodes()
        else:
            node_list = [child for child in self.children if child.volatile is False]
        for node in node_list:
            loaded = node.wait_until_loaded(timeout,
                                            raise_error,
                                            force_valid_count_greater_than_zero=False)
            if loaded is False:
                if element_in_iframe is True:
                    self.switch_to_default_content()
                return False
        else:
            if element_in_iframe is True:
                self.switch_to_default_content()
            return True

    def wait_until_value_is(self,
                            value: typing.Any,
                            timeout: typing.Union[int, float] = None,
                            raise_error: bool = True) -> bool:
        self.logger.debug(f"Starting wait_until_value_is for node: {self}")
        self.base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.base_case, settings.LARGE_TIMEOUT)

        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode value is not '{value}' after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self._get_value, timeout=timeout, expected=value, raise_error=raise_error)
        return success

    def wait_until_value_is_not(self,
                                value: typing.Any,
                                timeout: typing.Union[int, float] = None,
                                raise_error: bool = True) -> bool:
        self.logger.debug(f"Starting wait_until_value_is_not for node: {self}")
        self.base_case.wait_for_ready_state_complete(timeout)
        if timeout is None:
            timeout = base_settings.BaseSettings.apply_timeout_multiplier(self.base_case, settings.LARGE_TIMEOUT)

        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode value is '{value}' after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(
            self._get_value,
            timeout=timeout,
            expected=value,
            equals=False,
            raise_error=raise_error,
        )
        return success

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

    ################
    # Other actions
    ################
    def get_tag_name(self, timeout: typing.Union[int, float] = None) -> typing.Optional[str]:
        element = self.wait_for_web_element(timeout)
        if element is None:
            return None
        else:
            return element.tag_name

    ################
    # get/set value
    ################
    def _get_value(self) -> typing.Any:
        if self.wait_until_present(self.value_timeout) is None:
            return None

        for node in self.path:
            for name in self._valid_names_from_ancestor(node):
                method = getattr(node, f"get_{name}_value", None)
                if method is not None:
                    return method()

        return self.get_field_value()

    def _set_value(self, value: typing.Any) -> None:
        if value is None:
            return

        for node in self.path:
            for name in self._valid_names_from_ancestor(node):
                method = getattr(node, f"set_{name}_value", None)
                if method is not None:
                    method(value)
                    return

        self.set_field_value(value)

    @property
    def value(self) -> typing.Any:
        return self._get_value()

    @value.setter
    def value(self, value: typing.Any) -> None:
        self._set_value(value)

    def get_field_value(self) -> typing.Any:
        element = self.base_case.find_element(self.selector, self.by)
        tag_name = element.tag_name
        text = element.text
        element_type = element.get_attribute("type")
        if pombase.util.caseless_equal(tag_name, "input"):
            if isinstance(element_type, str) \
                    and pombase.util.caseless_text_in_texts(element_type, ["checkbox", "radio"]):
                return element.is_selected()
            elif text in [None, ""]:
                return element.get_attribute("value")
        if pombase.util.caseless_equal(tag_name, "select"):
            select = Select(element)
            selected: typing.List[WebElement] = select.all_selected_options
            if len(selected) == 1:
                return selected[0].text
            else:
                return [item.text for item in selected]

        return text

    def set_field_value(self, value: typing.Any) -> None:
        element = self.wait_for_web_element()
        tag_name = element.tag_name
        element_type = element.get_attribute("type")
        if pombase.util.caseless_equal(tag_name, "input"):
            if isinstance(element_type, str) and pombase.util.caseless_equal(element_type, "text"):
                element.send_keys(str(value))
            elif isinstance(element_type, str) and pombase.util.caseless_equal(element_type, "checkbox"):
                if value is True or (isinstance(value, str) and pombase.util.caseless_equal(value, "true")):
                    self.select_if_unselected()
                elif value is False or (isinstance(value, str) and pombase.util.caseless_equal(value, "false")):
                    self.unselect_if_selected()
                elif isinstance(value, str) and pombase.util.caseless_equal(value, "toggle"):
                    self.click()
                else:
                    raise Exception(
                        f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. Node: {self}",
                    )
            elif isinstance(element_type, str) and pombase.util.caseless_equal(element_type, "radio"):
                if value is True or (isinstance(value, str) and pombase.util.caseless_equal(value, "true")):
                    self.select_if_unselected()
                else:
                    raise Exception(
                        f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. Node: {self}",
                    )
            elif isinstance(element_type, str) and pombase.util.caseless_equal(element_type, "file"):
                self.choose_file(os.path.abspath(value))
            else:
                raise Exception(
                    f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. Node: {self}",
                )
        if pombase.util.caseless_equal(tag_name, "select"):
            select = Select(element)
            if isinstance(value, str):
                select.select_by_visible_text(value)
            elif isinstance(value, int):
                select.select_by_index(value)
            elif isinstance(value, list):
                if len(value) == 0:
                    select.deselect_all()
                else:
                    for item in value:
                        if isinstance(item, str):
                            select.select_by_visible_text(item)
                        elif isinstance(item, int):
                            select.select_by_index(item)
                        else:
                            raise Exception(
                                f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. "
                                f"Node: {self}",
                            )
        element.send_keys(str(value))

    ########
    # Alias
    ########
    def _full_name_from_ancestor(self, ancestor: WebNode = None) -> str:
        if ancestor is None:
            ancestor = self.root
        path = self.path
        index = path.index(ancestor)
        path = path[index:]
        all_names = [node.name for node in path if node.name is not None]
        if self.name is None:
            all_names.append(self._node_id)
        return self.separator.join(all_names)

    def _valid_names_from_ancestor(self, ancestor: WebNode = None) -> typing.List[str]:
        if self.name is None:
            # If name is None, consider [id, ] the only valid names_to_node
            return [self._node_id, ]

        full_name_chunks = self._full_name_from_ancestor(ancestor).split(self.separator)
        all_valid = []
        # possible combinations
        repeat = len(full_name_chunks) - 1
        name_combinations = list(itertools.product([True, False], repeat=repeat))
        # always include last name
        name_combinations = [combination + (True,) for combination in name_combinations]
        # sort possible combinations (highest True first, so "full_names_to_node" first)
        name_combinations.sort(key=lambda combination: combination.count(False))

        for combination in name_combinations:
            include_names = []
            for i, item in enumerate(combination):
                if item is False:
                    try:
                        int(full_name_chunks[i])
                    except ValueError:
                        pass
                    else:
                        continue
                if item is True:
                    include_names.append(full_name_chunks[i])
            name = self.separator.join(include_names)
            if self._check_name_from_ancestor(name) is True:
                all_valid.append(name)
        return all_valid

    def _minimal_name_from_ancestor(self, ancestor: WebNode = None) -> str:
        valid = self._valid_names_from_ancestor(ancestor)
        valid.sort(key=lambda name: len(name.split(self.separator)))
        return valid[0]

    def _check_name_from_ancestor(self, name: str, ancestor: WebNode = None) -> bool:
        if ancestor is None:
            ancestor = self.root
        try:
            found = ancestor.find_node(name)
        except AssertionError:
            return False
        if found == self:
            return True
        else:
            return False

    def _named_descendants(self) -> typing.List[WebNode]:
        named_descendants = list(anytree.search.findall(self, filter_=lambda n: n.name is not None))
        if self in named_descendants:
            named_descendants.remove(self)
        return named_descendants

    def __getattr__(self, item: str) -> WebNode:
        if item.startswith("_"):
            raise AttributeError(f"Attribute '{item}' not found for node: {self}")
        try:
            node = self.find_node(item)
        except AssertionError:
            raise AttributeError(f"Attribute '{item}' not found for node: {self}")
        return node

    ############
    # Fill Form
    ############
    def fill_form(self, **kwargs) -> dict:
        # ActionCommand
        self.logger.debug(f"Starting fill_form with kwargs='{kwargs}' for node: {self}")
        return_value = {}

        for kw, arg in kwargs.items():
            if arg is None:
                return_value[kw] = self.find_node(kw).value
            elif isinstance(arg, action.Action):
                arg.node = self
                return_value[kw] = arg.run()
            else:
                self.value = arg

        return return_value

    #######################
    # SeleniumBase actions
    #######################
    def click(self, timeout: typing.Union[int, float] = None, delay: int = 0) -> None:
        return self.base_case.click(self.selector, timeout=timeout, delay=delay)

    def slow_click(self, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.slow_click(self.selector, timeout=timeout)

    def double_click(self, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.double_click(self.selector, timeout=timeout)

    # def click_chain(self, timeout: typing.Union[int, float] = None, spacing: int = 0) -> None:
    #     return self.base_case.click_chain([self.full_selector, ], self.full_by, timeout=timeout, spacing=spacing)

    def type(self, text: str, timeout: typing.Union[int, float] = None, retry: bool = True) -> None:
        return self.base_case.type(self.selector, text, timeout=timeout, retry=retry)

    def add_text(self, text: typing.Union[str, int, float], timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.add_text(self.selector, text, timeout=timeout)

    def submit(self) -> None:
        return self.base_case.submit(self.selector)

    def clear(self, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.clear(self.selector, timeout=timeout)

    def is_text_visible(self, text: str) -> bool:
        return self.base_case.is_text_visible(text, self.selector)

    def get_text(self, timeout: typing.Union[int, float] = None) -> str:
        return self.base_case.get_text(self.selector, timeout=timeout)

    def get_attribute(self,
                      attribute: str,
                      timeout: typing.Union[int, float] = None,
                      hard_fail: bool = True) -> typing.Any:
        return self.base_case.get_attribute(
            self.selector,
            attribute,
            timeout=timeout,
            hard_fail=hard_fail,
        )

    def set_attribute(self, attribute: str, value: typing.Any, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.set_attribute(self.selector, attribute, value, timeout=timeout)

    def set_attributes(self, attribute: str, value: typing.Any) -> None:
        return self.base_case.set_attributes(self.selector, attribute, value)

    def remove_attribute(self, attribute: str, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.remove_attribute(self.selector, attribute, timeout=timeout)

    def remove_attributes(self, attribute: str) -> None:
        return self.base_case.remove_attributes(self.selector, attribute)

    # noinspection PyShadowingBuiltins
    def get_property_value(self, property: str, timeout: typing.Union[int, float] = None) -> typing.Any:
        return self.base_case.get_property_value(self.selector, property, timeout=timeout)

    def get_image_url(self, timeout: typing.Union[int, float] = None) -> str:
        return self.base_case.get_image_url(self.selector, timeout=timeout)

    def click_visible_elements(self, limit: int = 0, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.click_visible_elements(self.selector, limit=limit, timeout=timeout)

    def click_nth_visible_element(self, number: int, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.click_nth_visible_element(self.selector, number, timeout=timeout)

    def click_if_visible(self) -> None:
        return self.base_case.click_if_visible(self.selector)

    def is_selected(self, timeout: typing.Union[int, float] = None) -> bool:
        return self.base_case.is_selected(self.selector, timeout=timeout)

    def select_if_unselected(self) -> None:
        return self.base_case.select_if_unselected(self.selector)

    def unselect_if_selected(self) -> None:
        return self.base_case.unselect_if_selected(self.selector)

    def is_element_in_an_iframe(self) -> bool:
        return self.base_case.is_element_in_an_iframe(self.selector)

    def switch_to_frame_of_element(self) -> typing.Optional[str]:
        return self.base_case.switch_to_frame_of_element(self.selector)

    def hover_on_element(self) -> None:
        return self.base_case.hover_on_element(self.selector)

    def hover_and_click(self, click_node: typing.Union[str, WebNode], timeout: typing.Union[int, float] = None) -> None:
        if isinstance(click_node, str):
            click_node = self.find_node(click_node, descendants_only=False)
        return self.base_case.hover_and_click(self.selector, click_node.selector, timeout=timeout)

    def hover_and_double_click(self,
                               click_node: typing.Union[str, WebNode],
                               timeout: typing.Union[int, float] = None) -> None:
        if isinstance(click_node, str):
            click_node = self.find_node(click_node, descendants_only=False)
        return self.base_case.hover_and_double_click(self.selector, click_node.selector, timeout=timeout)

    def drag_and_drop(self,
                      drop_node: typing.Union[str, WebNode],
                      timeout: typing.Union[int, float] = None) -> None:
        if isinstance(drop_node, str):
            drop_node = self.find_node(drop_node, descendants_only=False)
        return self.base_case.drag_and_drop(self.selector, drop_node.selector, timeout=timeout)

    def select_option_by_text(self, option: str, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.select_option_by_text(self.selector, option, timeout=timeout)

    def select_option_by_index(self, option: int, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.select_option_by_index(self.selector, option, timeout=timeout)

    def select_option_by_value(self, option: str, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.select_option_by_value(self.selector, option, timeout=timeout)

    def switch_to_frame(self, timeout: typing.Union[int, float] = None):
        return self.base_case.switch_to_frame(self.selector, timeout)

    def bring_to_front(self) -> None:
        return self.base_case.bring_to_front(self.selector)

    def highlight_click(self, loops: int = 3, scroll: bool = True) -> None:
        return self.base_case.highlight_click(self.selector, loops=loops, scroll=scroll)

    def highlight_update_text(self, text: str, loops: int = 3, scroll: bool = True) -> None:
        return self.base_case.highlight_update_text(self.selector, text, loops=loops, scroll=scroll)

    def highlight(self, loops: int = 4, scroll: bool = True) -> None:
        return self.base_case.highlight(self.selector, loops=loops, scroll=scroll)

    def press_up_arrow(self, times: int = 1) -> None:
        return self.base_case.press_up_arrow(self.selector, times)

    def press_down_arrow(self, times: int = 1) -> None:
        return self.base_case.press_down_arrow(self.selector, times)

    def press_left_arrow(self, times: int = 1) -> None:
        return self.base_case.press_left_arrow(self.selector, times)

    def press_right_arrow(self, times: int = 1) -> None:
        return self.base_case.press_right_arrow(self.selector, times)

    def scroll_to(self, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.scroll_to(self.selector, timeout=timeout)

    def slow_scroll_to(self, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.slow_scroll_to(self.selector, timeout=timeout)

    def js_click(self, all_matches: bool = False) -> None:
        return self.base_case.js_click(self.selector, all_matches=all_matches)

    def js_click_all(self) -> None:
        return self.base_case.js_click_all(self.selector)

    def jquery_click(self) -> None:
        return self.base_case.jquery_click(self.selector)

    def jquery_click_all(self) -> None:
        return self.base_case.jquery_click_all(self.selector)

    def hide_element(self) -> None:
        return self.base_case.hide_element(self.selector)

    def hide_elements(self) -> None:
        return self.base_case.hide_elements(self.selector)

    def show_element(self) -> None:
        return self.base_case.show_element(self.selector)

    def show_elements(self) -> None:
        return self.base_case.show_elements(self.selector)

    def remove_element(self) -> None:
        return self.base_case.remove_element(self.selector)

    def remove_elements(self) -> None:
        return self.base_case.remove_elements(self.selector)

    def choose_file(self, file_path: os.PathLike, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.choose_file(self.selector, file_path, timeout=timeout)

    def save_element_as_image_file(self,
                                   file_name: os.PathLike,
                                   folder: os.PathLike = None,
                                   overlay_text: str = "") -> None:
        return self.base_case.save_element_as_image_file(self.selector, file_name, folder, overlay_text=overlay_text)

    def set_value(self, text: str, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.set_value(self.selector, text, timeout=timeout)

    def js_update_text(self, text: str, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.js_update_text(self.selector, text, timeout=timeout)

    def jquery_update_text(self, text: str, timeout: typing.Union[int, float] = None) -> None:
        return self.base_case.jquery_update_text(self.selector, text, timeout=timeout)

    def add_tour_step(self,
                      message: str,
                      name: str = None,
                      title: str = None,
                      theme: str = None,
                      alignment: str = None,
                      duration: typing.Union[int, float] = None) -> None:
        return self.base_case.add_tour_step(message,
                                            self.selector,
                                            name=name,
                                            title=title,
                                            theme=theme,
                                            alignment=alignment,
                                            duration=duration)

    def post_message_and_highlight(self, message) -> None:
        return self.base_case.post_message_and_highlight(message, self.selector)

    def find_text(self, text: str, timeout: typing.Union[int, float] = None) -> WebElement:
        return self.base_case.find_text(text, self.selector, timeout=timeout)

    def wait_for_exact_text_visible(self, text: str, timeout: typing.Union[int, float] = None) -> WebElement:
        return self.base_case.wait_for_exact_text_visible(text, self.selector, timeout=timeout)

    def assert_text(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.base_case.assert_text(text, self.selector, timeout=timeout)

    def assert_exact_text(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.base_case.assert_exact_text(text, self.selector, timeout=timeout)

    def wait_for_text_not_visible(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.base_case.wait_for_text_not_visible(text, self.selector, timeout=timeout)

    def assert_text_not_visible(self, text: str, timeout: typing.Union[int, float] = None) -> bool:
        return self.base_case.assert_text_not_visible(text, self.selector, timeout=timeout)
