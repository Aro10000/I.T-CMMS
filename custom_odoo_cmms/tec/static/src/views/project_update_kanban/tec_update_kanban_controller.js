/** @odoo-module */

import { KanbanController } from '@web/views/kanban/kanban_controller';
import { TecRightSidePanel } from '../../components/tec_right_side_panel/tec_right_side_panel';

export class TecUpdateKanbanController extends KanbanController {
    get className() {
        return super.className + ' o_controller_with_rightpanel';
    }
}

TecUpdateKanbanController.components = {
    ...KanbanController.components,
    TecRightSidePanel,
};
TecUpdateKanbanController.template = 'tec.TecUpdateKanbanView';
