/** @odoo-module **/

import { registry } from "@web/core/registry";
import { formView } from "@web/views/form/form_view";
import { TechProviderConfigFormRenderer } from "./tech_provider_config_form_renderer";


export const TechProviderConfigFormView = {
    ...formView,
    Renderer: TechProviderConfigFormRenderer,
};

registry.category("views").add("tech_provider_config_form", TechProviderConfigFormView);
