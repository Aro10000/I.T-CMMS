/** @odoo-module */

import { registry } from "@web/core/registry";
import { formViewWithHtmlExpander } from '../form_with_html_expander/form_view_with_html_expander';
import { TecTaskFormController } from './tec_task_form_controller';
import { TecTaskFormRenderer } from "./tec_task_form_renderer";

export const tecTaskFormView = {
    ...formViewWithHtmlExpander,
    Controller: TecTaskFormController,
    Renderer: TecTaskFormRenderer,
};

registry.category("views").add("tec_task_form", tecTaskFormView);
