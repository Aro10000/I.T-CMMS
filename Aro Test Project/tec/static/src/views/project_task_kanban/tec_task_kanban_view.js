/** @odoo-module */

import { registry } from "@web/core/registry";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { TecTaskKanbanModel } from "./tec_task_kanban_model";
import { TecTaskKanbanRenderer } from './tec_task_kanban_renderer';
import { TecControlPanel } from "../../components/tec_control_panel/tec_control_panel";

export const tecTaskKanbanView = {
    ...kanbanView,
    Model: TecTaskKanbanModel,
    Renderer: TecTaskKanbanRenderer,
    ControlPanel: TecControlPanel,
};

registry.category('views').add('tec_task_kanban', tecTaskKanbanView);
