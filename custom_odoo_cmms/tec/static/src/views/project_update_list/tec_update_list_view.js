/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { TecUpdateListController } from './tec_update_list_controller';

export const tecUpdateListView = {
    ...listView,
    Controller: TecUpdateListController,
};

registry.category('views').add('tec_update_list', tecUpdateListView);
