/** @odoo-module */

import { formView } from '@web/views/form/form_view';
import { TecSharingFormController } from './tec_sharing_form_controller';
import { TecSharingFormRenderer } from './tec_sharing_form_renderer';

formView.Controller = TecSharingFormController;
formView.Renderer = TecSharingFormRenderer;
