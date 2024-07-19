/** @odoo-module **/

import ListController from 'web.ListController';
import ListRenderer from 'web.ListRenderer';
import ListView from 'web.ListView';
import viewRegistry from 'web.view_registry';
import TecRightSidePanel from '@tec/js/right_panel/tec_right_panel';
import {
    RightPanelControllerMixin,
    RightPanelRendererMixin,
    RightPanelViewMixin,
} from '@tec/js/right_panel/tec_right_panel_mixin';

const TecUpdateListRenderer = ListRenderer.extend(RightPanelRendererMixin);

const TecUpdateListController = ListController.extend(RightPanelControllerMixin);

export const TecUpdateListView = ListView.extend(RightPanelViewMixin).extend({
    config: Object.assign({}, ListView.prototype.config, {
        Controller: TecUpdateListController,
        Renderer: TecUpdateListRenderer,
        RightSidePanel: TecRightSidePanel,
    }),
});

viewRegistry.add('tec_update_list', TecUpdateListView);
