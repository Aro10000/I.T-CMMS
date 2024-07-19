/** @odoo-module */

import { SelectionField } from '@web/views/fields/selection/selection_field';
import { registry } from '@web/core/registry';

import { STATUS_COLORS, STATUS_COLOR_PREFIX } from '../../utils/tec_utils';

export class TecStatusWithColorSelectionField extends SelectionField {
    setup() {
        super.setup();
        this.colorPrefix = STATUS_COLOR_PREFIX;
        this.colors = STATUS_COLORS;
    }

    get currentValue() {
        return this.props.value || this.options[0][0];
    }

    statusColor(value) {
        return this.colors[value] ? this.colorPrefix + this.colors[value] : "";
    }
}
TecStatusWithColorSelectionField.template = 'tec.TecStatusWithColorSelectionField';

registry.category('fields').add('status_with_color', TecStatusWithColorSelectionField);
