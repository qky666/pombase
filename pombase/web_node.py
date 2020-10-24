from __future__ import annotations

import anytree
import typing

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .pom_base_case import PomBaseCase
from .util import Util


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
                 is_template: bool = None,
                 template: typing.Union[str, WebNode] = None,
                 template_args: list = None,
                 template_kwargs: dict = None,
                 pom_base_case: PomBaseCase = None,
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
        self._is_template = is_template
        self._template = template
        self._template_args = template_args
        self._template_kwargs = template_kwargs
        self._pom_base_case = pom_base_case
        self._kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        super().__init__(parent=parent, children=children)

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
    def pom_base_case(self) -> PomBaseCase:
        if self._pom_base_case is None:
            return self.root.pom_base_case
        return self._pom_base_case

    @pom_base_case.setter
    def pom_base_case(self, value: typing.Optional[PomBaseCase]) -> None:
        self._pom_base_case = value

    ######################
    # Computed properties
    ######################
    @property
    def object_id(self) -> int:
        return id(self)

    @property
    def full_name(self) -> str:
        full_name = self.separator
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

    ##############
    # Validations
    ##############
    def _post_attach(self, parent: WebNode) -> None:
        super()._post_attach(parent)
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
            if Util.web_element_match_text_pattern(element,
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
                    if Util.web_element_match_text_pattern(element,
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
        elements = [Util.attach_canonical_xpath_and_node_to_web_element(element, self.pom_base_case.driver)
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
