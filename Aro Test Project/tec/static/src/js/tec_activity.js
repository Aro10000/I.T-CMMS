/** @odoo-module **/

import ActivityView from '@mail/js/views/activity/activity_view';
import { TecControlPanel } from '@tec/js/tec_control_panel';
import viewRegistry from 'web.view_registry';

const TecActivityView = ActivityView.extend({
    config: Object.assign({}, ActivityView.prototype.config, {
        ControlPanel: TecControlPanel,
    }),
});

viewRegistry.add('tec_activity', TecActivityView);
