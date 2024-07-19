/** @odoo-module */

import { ChatterContainer } from '../../components/chatter/chatter_container';
import { FormRenderer } from '@web/views/form/form_renderer';

export class TecSharingFormRenderer extends FormRenderer { }
TecSharingFormRenderer.components = {
    ...FormRenderer.components,
    ChatterContainer,
};
