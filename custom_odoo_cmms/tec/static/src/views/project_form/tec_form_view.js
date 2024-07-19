/** @odoo-module */

import { registry } from "@web/core/registry";
import { formViewWithHtmlExpander } from '../form_with_html_expander/form_view_with_html_expander';
import { TecFormRenderer } from "./tec_form_renderer";

export const tecFormView = {
    ...formViewWithHtmlExpander,
    Renderer: TecFormRenderer,
};

registry.category("views").add("tec_form", tecFormView);
