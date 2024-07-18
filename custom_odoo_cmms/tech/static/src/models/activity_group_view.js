/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'ActivityGroupView',
    recordMethods: {
        /**
         * @override
         */
        onClickFilterButton(ev) {
            const $el = $(ev.currentTarget);
            const data = _.extend({}, $el.data());
            if (data.res_model === "tech.event" && data.filter === "my") {
                this.activityMenuViewOwner.update({ isOpen: false });
                this.env.services['action'].doAction('tech.action_tech_event', {
                    additionalContext: {
                        default_mode: 'day',
                        search_default_mymeetings: 1,
                    },
                    clearBreadcrumbs: true,
                });
            } else {
                this._super.apply(this, arguments);
            }
        },
    },
});
