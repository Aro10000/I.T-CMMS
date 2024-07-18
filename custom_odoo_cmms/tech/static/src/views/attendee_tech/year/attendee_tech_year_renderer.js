/** @odoo-module **/

import { TechYearRenderer } from "@web/views/tech/tech_year/tech_year_renderer";
import { AttendeeTechYearPopover } from "@tech/views/attendee_tech/year/attendee_tech_year_popover";

export class AttendeeTechYearRenderer extends TechYearRenderer {}
AttendeeTechYearRenderer.components = {
    ...TechYearRenderer,
    Popover: AttendeeTechYearPopover,
};
