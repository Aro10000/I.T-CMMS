/** @odoo-module */

import { ListController } from '@web/views/list/list_controller';
import { TecRightSidePanel } from '../../components/tec_right_side_panel/tec_right_side_panel';

export class TecUpdateListController extends ListController {
    get className() {
        return super.className + ' o_controller_with_rightpanel';
    }
}

TecUpdateListController.components = {
    ...ListController.components,
    TecRightSidePanel,
};
TecUpdateListController.template = 'tec.TecUpdateListView';
