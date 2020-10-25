from __future__ import annotations

import typing
import os
import yaml
import anytree.importer

from . import web_node


class FileLoader:

    @staticmethod
    def load_node_from_file(file: os.PathLike = None) -> typing.Optional[web_node.WebNode]:
        if file is None or not os.path.isfile(file):
            return None

        with open(file, encoding="utf-8") as src_file:
            yaml_data = src_file.read()
        file_data = yaml.safe_load(yaml_data)
        node_importer = anytree.importer.DictImporter(web_node.WebNode)
        node: web_node.WebNode = node_importer.import_(file_data)
        required_name = os.path.splitext(os.path.basename(file))[0]
        if node.name is None:
            node.name = required_name
        else:
            assert node.name == required_name, \
                f"WebNode name should be '{required_name}' but name={node.name}. Node: {node}"
        # Convert to desired class the whole tree
        return node.replace_with_desired_class_node()
