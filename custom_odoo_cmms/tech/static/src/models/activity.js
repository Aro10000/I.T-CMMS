/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr } from '@mail/model/model_field';

registerPatch({
    name: 'Activity',
    modelMethods: {
        /**
         * @override
         */
        convertData(data) {
            const res = this._super(data);
            if ('tech_event_id' in data) {
                res.tech_event_id = data.tech_event_id[0];
            }
            return res;
        },
    },
    recordMethods: {
        /**
         * @override
         */
        async deleteServerRecord() {
            if (!this.tech_event_id){
                await this._super();
            } else {
                await this.messaging.rpc({
                    model: 'mail.activity',
                    method: 'unlink_w_meeting',
                    args: [[this.id]],
                });
                if (!this.exists()) {
                    return;
                }
                this.delete();
            }
        },
        /**
         * In case the activity is linked to a meeting, we want to open the
         * tech view instead.
         *
         * @override
         */
        async edit() {
            if (!this.tech_event_id){
                await this._super();
            } else {
                const action = await this.messaging.rpc({
                    model: 'mail.activity',
                    method: 'action_create_tech_event',
                    args: [[this.id]],
                });
                this.env.services.action.doAction(action);
            }
        },
    },
    fields: {
        tech_event_id: attr({
            default: false,
        }),
    },
});
