/** @odoo-module */

import { registry } from '@web/core/registry';
import { CharField } from '@web/views/fields/char/char_field';
import { formatChar } from '@web/views/fields/formatters';

class TecTaskNameWithSubtaskCountCharField extends CharField {
    get formattedSubtaskCount() {
        return formatChar(this.props.record.data.allow_subtasks && this.props.record.data.child_text || '');
    }
}

TecTaskNameWithSubtaskCountCharField.template = 'tec.TecTaskNameWithSubtaskCountCharField';

registry.category('fields').add('name_with_subtask_count', TecTaskNameWithSubtaskCountCharField);
