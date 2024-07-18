/** @odoo-module **/

import { TechCommonPopover } from "@web/views/tech/tech_common/tech_common_popover";
import { useService } from "@web/core/utils/hooks";
import { useAskRecurrenceUpdatePolicy } from "@tech/views/ask_recurrence_update_policy_hook";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class AttendezTechCommonPopover extends TechCommonPopover {
    setup() {
        super.setup();
        this.user = useService("user");
        this.orm = useService("orm");
        this.askRecurrenceUpdatePolicy = useAskRecurrenceUpdatePolicy();
        // Show status dropdown if user is in attendezs list
        if (this.isCurrentUserAttendez) {
            this.statusColors = {
                accepted: "text-success",
                declined: "text-danger",
                tentative: "text-muted",
                needsAction: "text-dark",
            };
            this.statusInfo = {};
            for (const selection of this.props.model.fields.attendez_status.selection) {
                this.statusInfo[selection[0]] = {
                    text: selection[1],
                    color: this.statusColors[selection[0]],
                };
            }
            this.selectedStatusInfo = this.statusInfo[this.props.record.attendezStatus];
        }
    }

    get isCurrentUserAttendez() {
        return this.props.record.rawRecord.partner_ids.includes(this.user.partnerId);
    }

    get isCurrentUserOrganizer() {
        return this.props.record.rawRecord.partner_id[0] === this.user.partnerId;
    }

    get isEventPrivate() {
        return this.props.record.rawRecord.privacy === "private";
    }

    get displayAttendezAnswerChoice() {
        return (
            this.props.record.rawRecord.partner_ids.some((partner) => partner !== this.user.partnerId) &&
            this.props.record.isCurrentPartner
        );
    }

    get isEventDetailsVisible() {
        return this.isEventPrivate ? this.isCurrentUserAttendez : true;
    }

    get isEventArchivable() {
        return false;
    }

    /**
     * @override
     */
    get isEventDeletable() {
        return super.isEventDeletable && this.isCurrentUserAttendez && !this.isEventArchivable;
    }

    /**
     * @override
     */
    get isEventEditable() {
        return this.isEventPrivate ? this.isCurrentUserAttendez : super.isEventEditable;
    }

    async changeAttendezStatus(selectedStatus) {
        const record = this.props.record;
        if (record.attendezStatus === selectedStatus) {
            return this.props.close();
        }
        let recurrenceUpdate = false;
        if (record.rawRecord.recurrency) {
            recurrenceUpdate = await this.askRecurrenceUpdatePolicy();
            if (!recurrenceUpdate) {
                return this.props.close();
            }
        }
        await this.env.services.orm.call(
            this.props.model.resModel,
            "change_attendez_status",
            [[record.id], selectedStatus, recurrenceUpdate],
        );
        await this.props.model.load();
        this.props.close();
    }

    async onClickArchive() {
        await this.props.model.archiveRecord(this.props.record);
    }
}
AttendezTechCommonPopover.components = {
    ...TechCommonPopover.components,
    Dropdown,
    DropdownItem,
};
AttendezTechCommonPopover.subTemplates = {
    ...TechCommonPopover.subTemplates,
    body: "tech.AttendezTechCommonPopover.body",
    footer: "tech.AttendezTechCommonPopover.footer",
};
