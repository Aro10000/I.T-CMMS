/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { TechFormController } from "@tech/views/tech_form/tech_form_controller";

export const TechFormView = {
    ...formView,
    Controller: TechFormController,
};

registry.category("views").add("tech_form", TechFormView);
