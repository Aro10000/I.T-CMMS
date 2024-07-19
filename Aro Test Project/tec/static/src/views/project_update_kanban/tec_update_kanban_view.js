/** @odoo-module */

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { TecUpdateKanbanController } from './tec_update_kanban_controller';

export const tecUpdateKanbanView = {
    ...kanbanView,
    Controller: TecUpdateKanbanController,
};

registry.category('views').add('tec_update_kanban', tecUpdateKanbanView);
