from __future__ import annotations

import collections
import functools
import typing
import anytree
import itertools
import logging
import selenium.webdriver.remote.webelement as webelement
from cssselect import xpath as css_xpath
from selenium.webdriver.common import by as selenium_by

import pombase.pom_base_case as pom_base_case
import pombase.types as types
import pombase.util as util

NodeCount = typing.Union[None, int, range, itertools.count, typing.Iterable[int]]
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


class WebNode(anytree.node.anynode.AnyNode):
    separator = "__"

    def __init__(self,
                 locator: Locator = None,
                 *,
                 parent: WebNode = None,
                 children: typing.Iterable[WebNode] = None,
                 name: str = None,
                 override_parent: PseudoLocator = None,
                 valid_count: NodeCount = range(2),
                 ignore_invisible: bool = True,
                 pbc: pom_base_case.PomBaseCase = None,
                 **kwargs: typing.Any,
                 ):
        if children is None:
            children = []

        override_parent = get_locator(override_parent) if override_parent is not None else None
        if override_parent is not None and locator is None:
            locator = override_parent
            override_parent = None

        if valid_count is None:
            valid_count = itertools.count()
        if isinstance(valid_count, int):
            valid_count = [valid_count]

        # locator and valid_count are related
        if locator is not None and locator.index is not None:
            new_valid_count = []
            if 0 in valid_count:
                new_valid_count.append(0)
            if 1 in valid_count:
                new_valid_count.append(1)
            assert len(new_valid_count) > 0, \
                f"WebNode locator index (not None) incompatible with valid_count: {valid_count}. Locator: {locator}"
            valid_count = new_valid_count

        super().__init__(
            locator=locator,
            # Delay parent and children, so validate() is called at the end
            # parent=parent,
            # children=children,
            name=name,
            override_parent=override_parent,
            valid_count=valid_count,
            ignore_invisible=ignore_invisible,
            _pbc=pbc,
            _kwargs=kwargs,
            **kwargs,
        )

        # This is redundant, but we want to help PyCharm
        locator: typing.Optional[Locator]
        self.locator = locator
        # self.parent: WebNode = parent
        # self.children: typing.Iterable[WebNode] = children
        self.name = name
        override_parent: typing.Optional[Locator]
        self.override_parent = override_parent
        valid_count: typing.Iterable[int]
        self.valid_count = valid_count
        self.ignore_invisible = ignore_invisible
        self._pbc = pbc
        self._kwargs = kwargs
        # for key, value in kwargs.items():
        #     setattr(self, key, value)

        # Util
        self.logger = logging.getLogger()

        # Init node
        self.init_node()

        # Validation -> Not here, but in _post_attach
        # self.validate()
        parent: typing.Optional[WebNode]
        self.parent = parent
        children: typing.Iterable[WebNode]
        self.children = children

    ######################
    # Computed properties
    ######################
    @property
    def max_valid_count(self) -> typing.Optional[int]:
        if type(self.valid_count) == itertools.count:
            return None
        else:
            return max(self.valid_count)

    @property
    def relevant_properties(self) -> typing.Dict[str]:
        return dict(
            locator=self.locator,
            name=self.name,
            override_parent=self.override_parent,
            valid_count=self.valid_count,
            ignore_invisible=self.ignore_invisible,
            pbc=self.pbc,
            **self._kwargs,
        )

    @property
    def pbc(self) -> typing.Optional[pom_base_case.PomBaseCase]:
        reversed_node_path: tuple[WebNode] = self.path[::-1]
        for node in reversed_node_path:
            if node._pbc is not None:
                return node._pbc
        else:
            return None

    ########
    # Print
    ########
    def __repr__(self):
        return self.full_name

    ############
    # Node name
    ############
    @property
    def full_name(self) -> str:
        names = [node.name for node in self.path if node.name is not None]
        return self.separator.join(names)

    def relative_name_of_descendant(self, descendant: WebNode) -> str:
        if self not in descendant.path:
            return descendant.full_name
        rel_name = descendant.full_name
        nearest_named = self.find_nearest_named_ancestor_or_self()
        if rel_name.startswith(nearest_named.full_name):
            rel_name = rel_name[len(nearest_named.full_name):]
            while rel_name.startswith(self.separator):
                rel_name = rel_name[len(self.separator):]
        return rel_name

    def relative_name_from_ascendant(self, ascendant: WebNode) -> str:
        return ascendant.relative_name_of_descendant(self)

    ##############
    # Validations
    ##############
    def _post_attach(self, parent: WebNode) -> None:
        super()._post_attach(parent)
        self.validate()
        parent.validate()
        self.validate_unique_descendant_names()
        parent.find_nearest_named_ancestor_or_self().validate_unique_descendant_names()

    def validate(self) -> None:
        if self.name is None:
            assert self.locator is not None, \
                f"WebNode validation error. WebNode.name and WebNode.locator can not be both None: " \
                f"name={self.name}, locator={self.locator}"
            assert 0 not in self.valid_count, \
                f"WebNode validation error. If WebNode.name is None, 0 should not be in WebNode.valid_count: " \
                f"name={self.name}, valid_count={self.valid_count}"

        if self.name is not None:
            assert len(self.name) > 0, \
                f"WebNode validation error. WebNode.name length should not be 0: name={self.name}"
            assert self.separator not in self.name, \
                f"WebNode validation error. WebNode.name should not include '{self.separator}': name={self.name}"
            try:
                int(self.name)
            except ValueError:
                pass
            else:
                assert False, \
                    f"WebNode validation error. WebNode.name can not be an int: name={self.name}"
            assert self.name.startswith("_") is False, \
                f"WebNode validation error. WebNode.name should start with '_': name={self.name}"
            assert self.name.endswith("_") is False, \
                f"WebNode validation error. WebNode.name should end with '_': name={self.name}"
            assert self.name.isidentifier() is True, \
                f"WebNode validation error. WebNode.name should be a valid identifier: name={self.name}"

        if self.locator is not None and self.locator.index is not None:
            for valid in self.valid_count:
                assert valid in [0, 1], \
                    f"WebNode validation error. WebNode.valid_count should be in [0, 1]: " \
                    f"index={self.locator.index}, valid_count={self.valid_count}"

    def validate_unique_descendant_names(self) -> None:
        nearest = self.find_nearest_named_ancestor_or_self()
        named: list[WebNode] = list(anytree.findall(nearest, lambda node: node.name is not None))
        if nearest in named:
            named.remove(nearest)
        named = [node for node in named if node.parent.find_nearest_named_ancestor_or_self() == nearest]
        for node in named:
            found = nearest._find_directly_descendant_from_nearest_named_ancestor(node.name)
            assert len(found) == 1, f"Found {len(found)} nodes with name '{node.name}' starting from node: {nearest}"
            found_node = found.pop()
            assert found_node == node, \
                f"Found one node with name '{node.name}', but it is not the expected node. \n" \
                f"Real: {found_node} \nExpected: {node}"

    def _find_directly_descendant_from_nearest_named_ancestor(self, name: str) -> set[WebNode]:
        nearest = self.find_nearest_named_ancestor_or_self()
        nodes: list[WebNode] = anytree.findall_by_attr(self, name)
        return {node for node in nodes if node.parent.find_nearest_named_ancestor_or_self() == nearest and node != self}

    ############
    # Init node
    ############
    def init_node(self) -> None:
        pass

    ################
    # Finding nodes
    ################
    def find_nearest_named_ancestor_or_self(self) -> WebNode:
        if self.is_root or self.name is not None:
            return self
        else:
            return self.parent.find_nearest_named_ancestor_or_self()

    def find_node(self, path: str, descendants_only: bool = True) -> WebNode:
        base_node = self
        found = base_node._find_descendant(path)
        assert len(found) <= 1, f"Found {len(found)} nodes with path '{path}' starting from node: {base_node}"
        if len(found) == 1:
            return found.pop()
        else:
            assert descendants_only is False and self.is_root is False, \
                f"Node with path '{path}' (only_descendants={descendants_only}) not found starting from node: {self}"
            while base_node.parent is not None:
                base_node_parent: WebNode = base_node.parent
                base_node = base_node_parent.find_nearest_named_ancestor_or_self()
                found = base_node._find_descendant(path)
                assert len(found) <= 1, f"Found {len(found)} nodes with path '{path}' starting from node: {base_node}"
                if len(found) == 1:
                    return found.pop()
            else:
                assert False, \
                    f"Node with path '{path}' (only_descendants={descendants_only}, whole tree has been searched) " \
                    f"not found starting from node: {self}"

    def _find_descendant(self, path: str) -> set[WebNode]:
        names = path.split(self.separator)
        while "" in names:
            names.remove("")
        assert len(names) > 0, f"Invalid path: {path}"
        nodes = set(anytree.findall_by_attr(self, names[0]))
        if self in nodes:
            nodes.remove(self)
        for name in names[1:]:
            new_nodes = set()
            for node in nodes:
                found = set(anytree.findall_by_attr(node, name))
                if node in found:
                    found.remove(node)
                new_nodes = new_nodes.union(found)
            nodes = new_nodes
        return nodes

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
        parent = self.parent
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

    #########################
    # Valid count & Multiple
    #########################
    @property
    def is_multiple(self) -> bool:
        if self.max_valid_count is None or self.max_valid_count > 1:
            return True
        else:
            return False

    def get_multiple_nodes(self) -> typing.Optional[list[WebNode]]:
        if self.is_multiple is False:
            return None
        if self.name is not None:
            # Remove previous nodes (if any) to avoid duplicated names
            i = 0
            prev_nodes = anytree.findall_by_attr(self.parent, f"{self.name}_{i}", maxlevel=2)
            while len(prev_nodes) > 0:
                for prev_node in prev_nodes:
                    prev_node: WebNode
                    prev_node.parent = None
                i = i + 1
                prev_nodes = anytree.findall_by_attr(self.parent, f"{self.name}_{i}", maxlevel=2)
        # Create new nodes
        nodes = []
        for i in range(self.count()):
            new_node = self.copy(recursive=True)
            new_node.locator = self.locator.copy(index=i)
            new_node.valid_count = range(2)
            if new_node.name is not None:
                new_node.name = f"{new_node.name}_{i}"
            new_node.parent = self.parent
            nodes.append(new_node)
        return nodes

    def _has_valid_count(self, force_count_not_zero: bool = False) -> bool:
        num_elements = self.count()
        if num_elements in self.valid_count and \
                ((force_count_not_zero is False) or (num_elements > 0)):
            return True
        else:
            return False

    def has_valid_count(self) -> bool:
        return self._has_valid_count()

    def wait_until_valid_count(self,
                               timeout: types.Number = None,
                               raise_error: bool = True,
                               force_count_not_zero: bool = True, ) -> bool:
        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode had not valid count after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self._has_valid_count,
                                     args=[force_count_not_zero, ],
                                     timeout=timeout,
                                     raise_error=raise_error)
        return success

    #########
    # Loaded
    #########
    def wait_until_loaded(self,
                          timeout: types.Number = None,
                          raise_error: bool = True,
                          force_count_not_zero: bool = True, ) -> bool:
        # Handle frames
        element_in_iframe = self.is_element_in_an_iframe()
        if element_in_iframe is True:
            for node in self.path[:-1]:
                node: WebNode
                if node.is_iframe() is True:
                    node.switch_to_frame(timeout)

        valid_count = self.wait_until_valid_count(timeout, raise_error, force_count_not_zero)
        if valid_count is False:
            if element_in_iframe is True:
                self.switch_to_default_content()
            return False

        children: typing.List[WebNode] = []
        if self.is_multiple:
            multiples = self.get_multiple_nodes()
            for node in multiples:
                node.wait_until_loaded(timeout, raise_error)
                children = children + node.children
        else:
            children = self.children
        for node in children:
            loaded = node.wait_until_loaded(timeout, raise_error, force_count_not_zero=False)
            if loaded is False:
                if element_in_iframe is True:
                    self.switch_to_default_content()
                return False
        else:
            if element_in_iframe is True:
                self.switch_to_default_content()
            return True

    ################
    # get/set value
    ################
    def _get_field_value(self, timeout: types.Number = None) -> typing.Any:
        for node in self.path:
            node: WebNode
            rel_name = node.relative_name_of_descendant(self)
            method = getattr(node, f"get_{rel_name}_field_value", None)
            if method is not None:
                return method(timeout)
        else:
            return self.get_field_value()

    def _set_field_value(self, value: typing.Any, timeout: types.Number = None) -> None:
        if value is None:
            return
        for node in self.path:
            node: WebNode
            rel_name = node.relative_name_of_descendant(self)
            method = getattr(node, f"set_{rel_name}_field_value", None)
            if method is not None:
                method(value, timeout)
                return
        else:
            self.set_field_value(value)

    @property
    def value(self) -> typing.Any:
        return self._get_field_value()

    @value.setter
    def value(self, value: typing.Any) -> None:
        self._set_field_value(value)

    def get_field_value(self, timeout: types.Number = None) -> typing.Any:
        tag_name = self.get_tag_name(timeout)
        text = self.get_text(timeout)
        if util.caseless_equal(tag_name, "input"):
            element_type = self.get_attribute("type", timeout, hard_fail=False)
            if isinstance(element_type, str) \
                    and util.caseless_text_in_texts(element_type, ["checkbox", "radio"]):
                return self.is_selected()
            elif text in [None, ""]:
                return self.get_attribute("value", timeout, hard_fail=False)
        elif util.caseless_equal(tag_name, "select"):
            return self.get_selected_options()
        else:
            return text

    def set_field_value(self, value: typing.Any, timeout: types.Number = None) -> None:
        tag_name = self.get_tag_name(timeout)
        element_type = self.get_attribute("type", timeout, hard_fail=False)
        if util.caseless_equal(tag_name, "input"):
            if isinstance(element_type, str) and util.caseless_equal(element_type, "text"):
                self.type(str(value), timeout, retry=True)
            elif isinstance(element_type, str) and util.caseless_equal(element_type, "checkbox"):
                if value is True or (isinstance(value, str)) and util.caseless_equal(value, "true"):
                    self.select_if_unselected()
                elif value is False or (isinstance(value, str) and util.caseless_equal(value, "false")):
                    self.unselect_if_selected()
                elif isinstance(value, str) and util.caseless_equal(value, "toggle"):
                    self.click()
                else:
                    raise Exception(
                        f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. Node: {self}",
                    )
            elif isinstance(element_type, str) and util.caseless_equal(element_type, "radio"):
                if value is True or (isinstance(value, str) and util.caseless_equal(value, "true")):
                    self.select_if_unselected()
                else:
                    raise Exception(
                        f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. Node: {self}",
                    )
            elif isinstance(element_type, str) and util.caseless_equal(element_type, "file"):
                self.choose_file(value)
            else:
                raise Exception(
                    f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. Node: {self}",
                )
        elif util.caseless_equal(tag_name, "select"):
            if isinstance(value, str):
                self.select_option_by_text(value, timeout)
            elif isinstance(value, int):
                self.select_option_by_index(value, timeout)
            elif isinstance(value, list):
                if len(value) == 0:
                    self.deselect_all_options(timeout)
                else:
                    for item in value:
                        if isinstance(item, str):
                            self.select_option_by_text(item, timeout)
                        elif isinstance(item, int):
                            self.select_option_by_index(item, timeout)
                        else:
                            raise Exception(
                                f"Do not know how to set value '{value}' to tag={tag_name} type={element_type}. "
                                f"Node: {self}",
                            )
        else:
            self.type(str(value), timeout)

    #######################
    # PomBaseCase methods
    #######################
    def count(self) -> int:
        return self.pbc.count(selector=self)

    def is_iframe(self, timeout: types.Number = None) -> bool:
        return self.pbc.is_iframe(selector=self, timeout=timeout)

    def switch_to_default_content(self) -> None:
        self.pbc.switch_to_default_content()

    def get_tag_name(self, timeout: types.Number = None) -> str:
        return self.pbc.get_tag_name(selector=self, timeout=timeout)

    def get_selected_options(self, timeout: types.Number = None) -> list[str]:
        return self.pbc.get_selected_options(selector=self, timeout=timeout)

    def deselect_all_options(self, timeout: types.Number = None) -> None:
        return self.pbc.deselect_all_options(selector=self, timeout=timeout)

    #######################
    # SeleniumBase methods
    #######################
    # TODO: Document these methods
    def click(self, timeout: types.Number = None, delay: int = 0) -> None:
        self.pbc.click(selector=self, timeout=timeout, delay=delay)

    def slow_click(self, timeout: types.Number = None) -> None:
        self.pbc.slow_click(selector=self, timeout=timeout)

    def double_click(self, timeout: types.Number = None) -> None:
        return self.pbc.double_click(selector=self, timeout=timeout)

    def click_chain(self, timeout: types.Number = None, spacing: int = 0) -> None:
        self.pbc.click_chain(selector=self, timeout=timeout, spacing=spacing)

    def add_text(self, text: str, timeout: types.Number = None) -> None:
        self.pbc.add_text(selector=self, text=text, timeout=timeout)

    def type(self, text: str, timeout: types.Number = None, retry: bool = False) -> None:
        self.pbc.type(selector=self, text=text, timeout=timeout, retry=retry)

    def submit(self) -> None:
        self.pbc.submit(selector=self)

    def clear(self, timeout: types.Number = None) -> None:
        self.pbc.clear(selector=self, timeout=timeout)

    def focus(self, timeout: types.Number = None) -> None:
        self.pbc.focus(selector=self, timeout=timeout)

    def is_element_present(self) -> bool:
        return self.pbc.is_element_present(selector=self)

    def is_element_visible(self) -> bool:
        return self.pbc.is_element_visible(selector=self)

    def is_element_enabled(self) -> bool:
        return self.pbc.is_element_enabled(selector=self)

    def is_text_visible(self, text: str) -> bool:
        return self.pbc.is_text_visible(text=text, selector=self)

    def get_text(self, timeout: types.Number = None) -> str:
        return self.pbc.get_text(selector=self, timeout=timeout)

    def get_attribute(self,
                      attribute: str,
                      timeout: types.Number = None,
                      hard_fail: bool = True, ) -> typing.Union[None, str, bool, int]:
        return self.pbc.get_attribute(selector=self, attribute=attribute, timeout=timeout, hard_fail=hard_fail)

    def set_attribute(self, attribute: str, value: typing.Any, timeout: types.Number = None) -> None:
        self.pbc.set_attribute(selector=self, attribute=attribute, value=value, timeout=timeout)

    def set_attributes(self, attribute: str, value: typing.Any) -> None:
        self.pbc.set_attributes(selector=self, attribute=attribute, value=value)

    def remove_attribute(self, attribute: str, timeout: types.Number = None) -> None:
        self.pbc.remove_attribute(selector=self, attribute=attribute, timeout=timeout)

    def remove_attributes(self, attribute: str) -> None:
        self.pbc.remove_attributes(selector=self, attribute=attribute)

    def get_property_value(self, property: str, timeout: types.Number = None) -> str:
        return self.pbc.get_property_value(selector=self, property=property, timeout=timeout)

    def get_image_url(self, timeout: types.Number = None) -> typing.Optional[str]:
        return self.pbc.get_image_url(selector=self, timeout=timeout)

    def find_elements(self, limit: int = 0) -> list[webelement.WebElement]:
        return self.pbc.find_elements(selector=self, limit=limit)

    def find_visible_elements(self, limit: int = 0) -> list[webelement.WebElement]:
        return self.pbc.find_visible_elements(selector=self, limit=limit)

    def click_visible_elements(self, limit: int = 0, timeout: types.Number = None) -> None:
        self.pbc.click_visible_elements(selector=self, limit=limit, timeout=timeout)

    def click_nth_visible_element(self, number, timeout: types.Number = None) -> None:
        self.pbc.click_nth_visible_element(selector=self, number=number, timeout=timeout)

    def click_if_visible(self) -> None:
        self.pbc.click_if_visible(selector=self)

    def is_selected(self, timeout: types.Number = None) -> bool:
        return self.pbc.is_selected(selector=self, timeout=timeout)

    def select_if_unselected(self) -> None:
        self.pbc.select_if_unselected(selector=self)

    def unselect_if_selected(self) -> None:
        self.pbc.unselect_if_selected(selector=self)

    def is_element_in_an_iframe(self) -> bool:
        return self.pbc.is_element_in_an_iframe(selector=self)

    def switch_to_frame_of_element(self) -> typing.Optional[str]:
        return self.pbc.switch_to_frame_of_element(selector=self)

    def hover_on_element(self) -> None:
        self.pbc.hover_on_element(selector=self)

    def hover_and_click(self,
                        click_selector: typing.Union[str, WebNode],
                        click_by: str = None,
                        timeout: types.Number = None, ) -> webelement.WebElement:
        return self.pbc.hover_and_click(
            hover_selector=self,
            click_selector=click_selector,
            click_by=click_by,
            timeout=timeout,
        )

    def hover_and_double_click(self,
                               click_selector: typing.Union[str, WebNode],
                               click_by: str = None,
                               timeout: types.Number = None, ) -> webelement.WebElement:
        return self.pbc.hover_and_double_click(
            hover_selector=self,
            click_selector=click_selector,
            click_by=click_by,
            timeout=timeout,
        )

    def drag_and_drop(self,
                      drop_selector: typing.Union[str, WebNode],
                      drop_by: str = None,
                      timeout: types.Number = None, ) -> webelement.WebElement:
        return self.pbc.drag_and_drop(
            drag_selector=self,
            drop_selector=drop_selector,
            drop_by=drop_by,
            timeout=timeout,
        )

    def drag_and_drop_with_offset(self, x: int, y: int, timeout: types.Number = None) -> webelement.WebElement:
        return self.pbc.drag_and_drop_with_offset(selector=self, x=x, y=y, timeout=timeout)

    def select_option_by_text(self, option: str, timeout: types.Number = None) -> None:
        self.pbc.select_option_by_text(dropdown_selector=self, option=option, timeout=timeout)

    def select_option_by_index(self, option: int, timeout: types.Number = None) -> None:
        self.pbc.select_option_by_index(dropdown_selector=self, option=option, timeout=timeout)

    def select_option_by_value(self, option: typing.Union[str, int], timeout: types.Number = None) -> None:
        self.pbc.select_option_by_value(dropdown_selector=self, option=option, timeout=timeout)

    def switch_to_frame(self, timeout: types.Number = None) -> None:
        self.pbc.switch_to_frame(frame=self, timeout=timeout)

    def bring_to_front(self) -> None:
        self.pbc.bring_to_front(selector=self)

    def highlight_click(self, loops: int = 3, scroll: bool = True) -> None:
        self.pbc.highlight_click(selector=self, loops=loops, scroll=scroll)

    def highlight_update_text(self, text: str, loops: int = 3, scroll: bool = True) -> None:
        self.pbc.highlight_update_text(selector=self, text=text, loops=loops, scroll=scroll)

    def highlight(self, loops=None, scroll: bool = True) -> None:
        self.pbc.highlight(selector=self, loops=loops, scroll=scroll)

    def press_up_arrow(self="html", times: int = 1) -> None:
        self.pbc.press_up_arrow(selector=self, times=times)

    def press_down_arrow(self="html", times: int = 1) -> None:
        self.pbc.press_down_arrow(selector=self, times=times)

    def press_left_arrow(self="html", times: int = 1) -> None:
        self.pbc.press_left_arrow(selector=self, times=times)

    def press_right_arrow(self="html", times: int = 1) -> None:
        self.pbc.press_right_arrow(selector=self, times=times)

    def scroll_to(self, timeout: types.Number = None) -> None:
        self.pbc.scroll_to(selector=self, timeout=timeout)

    def slow_scroll_to(self, timeout: types.Number = None) -> None:
        self.pbc.slow_scroll_to(selector=self, timeout=timeout)

    def js_click(self, all_matches: bool = False) -> None:
        self.pbc.js_click(selector=self, all_matches=all_matches)

    def js_click_all(self) -> None:
        self.pbc.js_click_all(selector=self)

    def jquery_click(self) -> None:
        self.pbc.jquery_click(selector=self)

    def jquery_click_all(self) -> None:
        self.pbc.jquery_click_all(selector=self)

    def hide_element(self) -> None:
        self.pbc.hide_element(selector=self)

    def hide_elements(self) -> None:
        self.pbc.hide_elements(selector=self)

    def show_element(self) -> None:
        self.pbc.show_element(selector=self)

    def show_elements(self) -> None:
        self.pbc.show_elements(selector=self)

    def remove_element(self) -> None:
        self.pbc.remove_element(selector=self)

    def remove_elements(self) -> None:
        self.pbc.remove_elements(selector=self)

    def choose_file(self, file_path, timeout: types.Number = None) -> None:
        self.pbc.choose_file(selector=self, file_path=file_path, timeout=timeout)

    def set_value(self, text: str, timeout: types.Number = None) -> None:
        self.pbc.set_value(selector=self, text=text, timeout=timeout)

    def js_update_text(self, text: str, timeout: types.Number = None) -> None:
        self.pbc.js_update_text(selector=self, text=text, timeout=timeout)

    def jquery_update_text(self, text: str, timeout: types.Number = None) -> None:
        self.pbc.jquery_update_text(selector=self, text=text, timeout=timeout)

    def post_message_and_highlight(self, message) -> None:
        self.pbc.post_message_and_highlight(message, self)

    def get_element(self, timeout: types.Number = None) -> webelement.WebElement:
        return self.pbc.get_element(selector=self, timeout=timeout)

    def assert_element_present(self, timeout: types.Number = None) -> bool:
        return self.pbc.assert_element_present(selector=self, timeout=timeout)

    def find_element(self, timeout: types.Number = None) -> webelement.WebElement:
        return self.pbc.find_element(selector=self, timeout=timeout)

    def assert_element(self, timeout: types.Number = None) -> bool:
        return self.pbc.assert_element(selector=self, timeout=timeout)

    def wait_for_exact_text_visible(self,
                                    text: str,
                                    timeout: types.Number = None) -> typing.Union[bool, webelement.WebElement]:
        return self.pbc.wait_for_exact_text_visible(text=text, selector=self, timeout=timeout)

    def find_text(self, text: str, timeout: types.Number = None) -> typing.Union[bool, webelement.WebElement]:
        return self.pbc.find_text(text=text, selector=self, timeout=timeout)

    def assert_text(self, text: str, timeout: types.Number = None) -> bool:
        return self.pbc.assert_text(text=text, selector=self, timeout=timeout)

    def assert_exact_text(self, text: str, timeout: types.Number = None) -> bool:
        return self.pbc.assert_exact_text(text=text, selector=self, timeout=timeout)

    def wait_for_element_absent(self, timeout: types.Number = None) -> bool:
        return self.pbc.wait_for_element_absent(selector=self, timeout=timeout)

    def assert_element_absent(self, timeout: types.Number = None) -> bool:
        return self.pbc.assert_element_absent(selector=self, timeout=timeout)

    def wait_for_element_not_visible(self, timeout: types.Number = None) -> bool:
        return self.pbc.wait_for_element_not_visible(selector=self, timeout=timeout)

    def assert_element_not_visible(self, timeout: types.Number = None) -> bool:
        return self.pbc.assert_element_not_visible(selector=self, timeout=timeout)

    def wait_for_text_not_visible(self, text: str, timeout: types.Number = None) -> bool:
        return self.pbc.wait_for_text_not_visible(text=text, selector=self, timeout=timeout)

    def assert_text_not_visible(self, text: str, timeout: types.Number = None) -> bool:
        return self.pbc.assert_text_not_visible(text=text, selector=self, timeout=timeout)

    def deferred_assert_element(self, timeout: types.Number = None) -> bool:
        return self.pbc.deferred_assert_element(selector=self, timeout=timeout)

    def deferred_assert_text(self, text: str, timeout: types.Number = None) -> bool:
        return self.pbc.deferred_assert_text(text=text, selector=self, timeout=timeout)


def node_from(selector: typing.Union[str, WebNode], by: str = None) -> WebNode:
    if isinstance(selector, WebNode):
        return selector
    else:
        return WebNode(Locator(selector, by))


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
    locators: list[Locator] = [get_locator(loc) for loc in locators]
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
    elif isinstance(obj, WebNode):
        return obj.locator
    elif isinstance(obj, str):
        return Locator(obj)
    elif isinstance(obj, dict):
        return Locator(**obj)
    elif isinstance(obj, typing.Iterable):
        return Locator(*obj)
    else:
        assert False, f"Can not get object as a Locator: {obj}"


PseudoLocator = typing.Union[Locator, str, dict, typing.Iterable, WebNode]
