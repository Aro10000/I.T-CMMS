/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";

const { Component } = owl;

export class AskRecurrenceUpdatePolicyDialog extends Component {
    setup() {
        this.possibleValues = {
            self_only: {
                checked: true,
                label: this.env._t("This event"),
            },
            future_events: {
                checked: false,
                label: this.env._t("This and following events"),
            },
            all_events: {
                checked: false,
                label: this.env._t("All events"),
            },
        };
    }

    get selected() {
        return Object.entries(this.possibleValues).find(state => state[1].checked)[0];
    }

    set selected(val) {
        this.possibleValues[this.selected].checked = false;
        this.possibleValues[val].checked = true;
    }

    confirm() {
        this.props.confirm(this.selected);
        this.props.close();
    }
}
AskRecurrenceUpdatePolicyDialog.template = "tech.AskRecurrenceUpdatePolicyDialog";
AskRecurrenceUpdatePolicyDialog.components = {
    Dialog,
};
