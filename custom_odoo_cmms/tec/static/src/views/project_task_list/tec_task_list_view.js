/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from '@web/views/list/list_view';
import { TecControlPanel } from "../../components/tec_control_panel/tec_control_panel";
import { TecTaskListController } from './tec_task_list_controller';

export const tecTaskListView = {
    ...listView,
    Controller: TecTaskListController,
    ControlPanel: TecControlPanel,
};

registry.category("views").add("tec_task_list", tecTaskListView);
