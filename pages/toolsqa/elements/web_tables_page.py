from __future__ import annotations

from pombase import SingleWebNode, TableNode, NumberType, wait_until
from overrides import overrides
from pages.toolsqa.web_concept_page import WebConceptPage


class RowActionNode(SingleWebNode):
    @overrides
    def init_node(self) -> None:
        super().init_node()

        self.swn_edit = SingleWebNode("span[title=Edit]", required=True)
        self.swn_delete = SingleWebNode("span[title=Delete]", required=True)


class WebTablesPage(WebConceptPage):
    # TODO: Remove this
    # default_name = "pn_toolsqa_web_tables"
    title = "Web Tables"
    expected_table_columns = ["First Name", "Last Name", "Age", "Email", "Salary", "Department", "Action"]

    @overrides
    def init_node(self) -> None:
        super().init_node()

        self.swn_table_wrapper = SingleWebNode("div.web-tables-wrapper", required=True)
        self.swn_table_wrapper__swn_add = SingleWebNode("button#addNewRecordButton", required=True)
        self.swn_table_wrapper__swn_search_box = SingleWebNode("input#searchBox", required=True)
        self.swn_table_wrapper__swn_table = TableNode(
            "div.rt-table",
            required=True,
            header_row_locator="div.rt-thead div.rt-tr",
            header_cell_locator="div.rt-th",
            data_row_locator="div.rt-tbody div.rt-tr",
            data_cell_locator="div.rt-td",
        )

    @overrides
    def override_wait_until_loaded(self, timeout: NumberType = None) -> None:
        super().override_wait_until_loaded(timeout)

        table = self.swn_table_wrapper__swn_table

        # Table Columns
        wait_until(
            table.get_header_cells_texts,
            args=[timeout, ],
            timeout=timeout,
            expected=self.expected_table_columns,
            raise_error="Incorrect columns",
        )

        # Row Actions exist for each row
        last_name_column_index = table.get_header_cell_index("Last Name", timeout)
        action_column_index = table.get_header_cell_index("Action", timeout)
        for i in range(len(table.mwn_data_rows.get_multiple_nodes())):
            last_name_txt = table.get_data_cell(i, last_name_column_index, timeout).get_text(timeout).strip()
            actions_cell_node = table.get_data_cell(i, action_column_index, timeout)
            if len(last_name_txt) > 0:
                RowActionNode("div.action-buttons", parent=actions_cell_node, required=True)
                # actions_cell_node has new child, so wait_until_loaded_succeeded to wait for this new child
                actions_cell_node.wait_until_loaded_succeeded(timeout)

    def delete_row(self, index: int = 0) -> None:
        table = self.swn_table_wrapper__swn_table
        action_cell_node = table.get_data_cell(index, "Action")
        row_action_node = RowActionNode("div.action-buttons", required=True, parent=action_cell_node)
        action_cell_node.wait_until_loaded_succeeded()
        row_action_node.swn_delete.click()
