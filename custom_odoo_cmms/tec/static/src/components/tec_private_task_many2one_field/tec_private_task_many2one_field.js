/** @odoo-module */

import { registry } from '@web/core/registry';
import { Many2OneField } from '@web/views/fields/many2one/many2one_field';

export class TecPrivateTaskMany2OneField extends Many2OneField { }
TecPrivateTaskMany2OneField.template = 'tec.TecPrivateTaskMany2OneField';

registry.category('fields').add('tec_private_task', TecPrivateTaskMany2OneField);
