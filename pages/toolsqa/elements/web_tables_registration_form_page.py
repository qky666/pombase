from __future__ import annotations

from pombase import SingleWebNode, NumberType, PageNode
from overrides import overrides


class WebTablesRegistrationFormPage(PageNode):
    @overrides
    def init_node(self) -> None:
        super().init_node()

        self.swn_registration_form = SingleWebNode("div.modal-content", required=True)
        self.swn_registration_form__swn_modal_title = SingleWebNode("div#registration-form-modal", required=True)
        self.swn_registration_form__swn_first_name = SingleWebNode("input#firstName", required=True)
        self.swn_registration_form__swn_last_name = SingleWebNode("input#lastName", required=True)
        self.swn_registration_form__swn_email = SingleWebNode("input#userEmail", required=True)
        self.swn_registration_form__swn_age = SingleWebNode("input#age", required=True)
        self.swn_registration_form__swn_salary = SingleWebNode("input#salary", required=True)
        self.swn_registration_form__swn_department = SingleWebNode("input#department", required=True)
        # buttons
        self.swn_registration_form__swn_close = SingleWebNode("button.close", required=True)
        self.swn_registration_form__swn_submit = SingleWebNode("button#submit", required=True)

    @overrides
    def override_wait_until_loaded(self, timeout: NumberType = None) -> None:
        super().override_wait_until_loaded(timeout)

        self.swn_registration_form__swn_modal_title\
            .wait_until_field_value_succeeded("Registration Form", timeout=timeout)
