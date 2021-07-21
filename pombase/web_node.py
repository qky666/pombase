from __future__ import annotations
import typing
import anytree
import itertools
import logging
import selenium.webdriver.remote.webelement as webelement

import pombase.locator as pb_locator
import pombase.pom_base_case as pom_base_case
import pombase.types as types
import pombase.util as util

NodeCount = typing.Union[None, int, range, itertools.count, typing.Iterable[int]]


def node_from(selector: typing.Union[str, WebNode], by: str = None) -> WebNode:
    if isinstance(selector, WebNode):
        return selector
    else:
        return WebNode(pb_locator.Locator(selector, by))


class WebNode(anytree.node.anynode.AnyNode):
    separator = "__"

    def __init__(self,
                 locator: pb_locator.Locator = None,
                 *,
                 parent: WebNode = None,
                 children: typing.Iterable[WebNode] = None,
                 name: str = None,
                 override_parent: pb_locator.PseudoLocator = None,
                 valid_count: NodeCount = range(2),
                 ignore_invisible: bool = True,
                 pbc: pom_base_case.PomBaseCase = None,
                 **kwargs: typing.Any,
                 ):
        if children is None:
            children = []

        override_parent = pb_locator.get_locator(override_parent) if override_parent is not None else None
        if override_parent is not None and locator is None:
            locator = override_parent
            override_parent = None

        if valid_count is None:
            valid_count = itertools.count()
        if isinstance(valid_count, int):
            valid_count = [valid_count]

        # locator and valid_count are related
        if self.locator is not None and self.locator.index is not None:
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
        locator: typing.Optional[pb_locator.Locator]
        self.locator = locator
        # self.parent: WebNode = parent
        # self.children: typing.Iterable[WebNode] = children
        self.name = name
        override_parent: typing.Optional[pb_locator.Locator]
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
    def max_count(self) -> typing.Optional[int]:
        if type(self.valid_count) == itertools.count:
            return None
        else:
            return max(self.valid_count)

    @property
    def is_multiple(self) -> bool:
        if self.max_count is None or self.max_count > 1:
            return True
        else:
            return False

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
    def full_name(self) -> str:
        names = [node.name for node in self.path if node.name is not None]
        return self.separator.join(names)

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
    def get_multiple_nodes(self) -> typing.Optional[list[WebNode]]:
        if self.is_multiple is False:
            return None
        nodes = []
        for i in range(self.count()):
            new_node = self.copy(recursive=True)
            new_node.locator = self.locator.copy(index=i)
            if new_node.name is not None:
                new_node.name = f"{new_node.name}_{i}"
            new_node.parent = self.parent
            nodes.append(new_node)
        return nodes

    def _has_valid_count(self, force_valid_count_not_zero: bool = False) -> bool:
        num_elements = self.count()
        if num_elements in self.valid_count and \
                ((force_valid_count_not_zero is False) or (num_elements > 0)):
            return True
        else:
            return False

    def has_valid_count(self) -> bool:
        return self._has_valid_count()

    def wait_until_valid_count(self,
                               timeout: typing.Union[int, float] = None,
                               raise_error: bool = True,
                               force_valid_count_not_zero: bool = True, ) -> bool:
        plural = "s" if timeout == 1 or timeout == 1.0 else ""
        raise_error = f"WebNode had not valid count after {timeout} second{plural}: {self}" \
            if raise_error is True else None
        success, _ = util.wait_until(self._has_valid_count,
                                     args=[force_valid_count_not_zero, ],
                                     timeout=timeout,
                                     raise_error=raise_error)
        return success

    #######################
    # PomBaseCase methods
    #######################
    def count(self) -> int:
        return self.pbc.count(selector=self)

    def is_iframe(self, timeout: types.Number = None) -> bool:
        return self.pbc.is_iframe(self, timeout=timeout)

    def switch_to_default_content(self) -> None:
        self.pbc.switch_to_default_content()

    #######################
    # SeleniumBase methods
    #######################
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
