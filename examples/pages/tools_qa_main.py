from pombase.web_node import WebNode


class ToolsQaMain(WebNode):

    def init_node(self) -> None:
        self.node_link_home = WebNode("a[href='https://demoqa.com']", valid_count=1)
