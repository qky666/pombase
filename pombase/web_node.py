from __future__ import annotations
import typing
import anytree
import itertools
import logging

import pombase.locator as pb_locator

NodeCount = typing.Union[None, int, range, itertools.count, typing.Iterable[int]]


class WebNode(anytree.node.anynode.AnyNode):
    NAME_SEPARATOR = "__"

    def __init__(self,
                 locator: pb_locator.Locator = None,
                 *,
                 parent: WebNode = None,
                 children: typing.Iterable[WebNode] = None,
                 name: str = None,
                 override_parent: pb_locator.PseudoLocator = None,
                 valid_count: NodeCount = range(2),
                 ignore_invisible: bool = True,
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
            override_parent=self.override_parent,
            valid_count=self.valid_count,
            ignore_invisible=self.ignore_invisible,
            **self._kwargs,
        )

    @property
    def full_name(self) -> str:
        names = [node.name for node in self.path if node.name is not None]
        return self.NAME_SEPARATOR.join(names)

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
            assert self.NAME_SEPARATOR not in self.name, \
                f"WebNode validation error. WebNode.name should not include '{self.NAME_SEPARATOR}': name={self.name}"
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
        named: typing.List[WebNode] = list(anytree.findall(nearest, lambda node: node.name is not None))
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

    def _find_directly_descendant_from_nearest_named_ancestor(self, name: str) -> typing.Set[WebNode]:
        nearest = self.find_nearest_named_ancestor_or_self()
        nodes: typing.List[WebNode] = anytree.findall_by_attr(self, name)
        return {node for node in nodes if node.parent.find_nearest_named_ancestor_or_self() == nearest and node != self}

    def _find_descendant(self, path: str) -> typing.Set[WebNode]:
        names = path.split(self.NAME_SEPARATOR)
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
