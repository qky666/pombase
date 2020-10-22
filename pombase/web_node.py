from __future__ import annotations

import anytree
import typing

from seleniumbase.fixtures.base_case import By


class WebNode(anytree.node.anynode.AnyNode):

    def __init__(self,
                 *,
                 parent: WebNode = None,
                 children: typing.Iterable[WebNode] = None,
                 name: str = None,
                 locator: str = None,  # Allow "id=my_selector", etc.
                 order: int = None,
                 text_match: str = None,  # Allow * and ? (\*, \?)
                 use_regexp_in_text_match: bool = None,
                 override_parent_selector: typing.Union[str, bool] = None,  # If True, use "css selector=html"
                 should_be_present: bool = None,
                 should_be_visible: bool = None,
                 is_multiple: bool = None,
                 is_template: bool = None,
                 template: typing.Union[str, WebNode] = None,
                 template_args: list = None,
                 template_kwargs: dict = None,
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
        self._text_match = text_match
        self._use_regexp_in_text_match = use_regexp_in_text_match
        self._override_parent_selector = override_parent_selector
        self._should_be_present = should_be_present
        self._should_be_visible = should_be_visible
        self._is_multiple = is_multiple
        self._is_template = is_template
        self._template = template
        self._template_args = template_args
        self._template_kwargs = template_kwargs
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

    # text_match
    @property
    def text_match(self) -> typing.Optional[str]:
        if self._text_match is None:
            if self.template is not None and self.template.text_match is not None:
                return self.template.text_match.format(*self.template_args, **self.template_kwargs)
        return self._text_match

    @text_match.setter
    def text_match(self, value: typing.Optional[str]) -> None:
        self._text_match = value
        self.validate()

    # use_regexp_in_text
    @property
    def use_regexp_in_text(self) -> bool:
        if self._use_regexp_in_text_match is None:
            if self.template is not None and self.template.use_regexp_in_text is not None:
                return self.template.use_regexp_in_text
            return False
        return self._use_regexp_in_text_match

    @use_regexp_in_text.setter
    def use_regexp_in_text(self, value: typing.Optional[bool]) -> None:
        self._use_regexp_in_text_match = value
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

    def selector(self) -> str:
        return self.selector_by_tuple()[0]

    def by(self) -> str:
        return self.selector_by_tuple()[1]

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

        if self.use_regexp_in_text is True:
            assert self.text_match is not None, \
                f"WebNode validation error: use_regexp_in_text={self.use_regexp_in_text}, text_match={self.text_match}"

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
        for i in range(1, len(names)):
            name = names[i]
            new_nodes = []
            for pre_node in nodes:
                new_nodes.append(anytree.findall_by_attr(pre_node, name))
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
