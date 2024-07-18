/** @odoo-module **/

import { TechController } from "@web/views/tech/tech_controller";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

export class AttendeeTechController extends TechController {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.user = useService("user");
        this.orm = useService("orm");
        onWillStart(async () => {
            this.isSystemUser = await this.user.hasGroup('base.group_system');
        });
    }

    onClickAddButton() {
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'tech.event',
            views: [[false, 'form']],
        }, {
            additionalContext: this.props.context,
        });
    }

    /**
     * @override
     *
     * If the event is deleted by the organizer, the event is deleted, otherwise it is declined.
     */
    deleteRecord(record) {
        if (this.user.partnerId === record.attendeeId && this.user.partnerId === record.rawRecord.partner_id[0]) {
            super.deleteRecord(...arguments);
        } else {
            // Decline event
            this.orm.call(
                "tech.attendee",
                "do_decline",
                [record.techAttendeeId],
            ).then(this.model.load.bind(this.model));
        }
    }

    configureTechProviderSync(providerName) {
        this.actionService.doAction({
            name: this.env._t('Connect your Tech'),
            type: 'ir.actions.act_window',
            res_model: 'tech.provider.config',
            views: [[false, "form"]],
            view_mode: "form",
            target: 'new',
            context: {
                'default_external_tech_provider': providerName,
                'dialog_size': 'medium',
            }
        });
    }
}
AttendeeTechController.template = "tech.AttendeeTechController";
