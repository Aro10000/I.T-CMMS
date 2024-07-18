/** @odoo-module **/

import { registry } from "@web/core/registry";
import { techView } from "@web/views/tech/tech_view";
import { AttendezTechController } from "@tech/views/attendee_tech/attendee_tech_controller";
import { AttendezTechModel } from "@tech/views/attendee_tech/attendee_tech_model";
import { AttendezTechRenderer } from "@tech/views/attendee_tech/attendee_tech_renderer";

export const attendeeTechView = {
    ...techView,
    Controller: AttendezTechController,
    Model: AttendezTechModel,
    Renderer: AttendezTechRenderer,
    buttonTemplate: "tech.AttendezTechController.controlButtons",
};

registry.category("views").add("attendee_tech", attendeeTechView);
