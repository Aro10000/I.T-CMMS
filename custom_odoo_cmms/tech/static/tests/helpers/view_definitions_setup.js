/** @odoo-module **/

import { registry } from '@web/core/registry';

const viewArchsRegistry = registry.category('bus.view.archs');
const techArchsRegistry = viewArchsRegistry.category('tech');

techArchsRegistry.add('default', '<tech date_start="start"/>');
