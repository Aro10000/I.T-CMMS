/** @odoo-module */

import { ConfirmationDialog } from '@web/core/confirmation_dialog/confirmation_dialog';

export class TecStopRecurrenceConfirmationDialog extends ConfirmationDialog {
    _continueRecurrence() {
        if (this.props.continueRecurrence) {
            this.props.continueRecurrence();
        }
        this.props.close();
    }
}
TecStopRecurrenceConfirmationDialog.template = 'tec.TecStopRecurrenceConfirmationDialog';
TecStopRecurrenceConfirmationDialog.props.continueRecurrence = { type: Function, optional: true };
