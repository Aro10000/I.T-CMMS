/** @odoo-module **/

import { TechRenderer } from "@web/views/tech/tech_renderer";
import { AttendeeTechCommonRenderer } from "@tech/views/attendee_tech/common/attendee_tech_common_renderer";
import { AttendeeTechYearRenderer } from "@tech/views/attendee_tech/year/attendee_tech_year_renderer";

export class AttendeeTechRenderer extends TechRenderer {}
AttendeeTechRenderer.components = {
    ...TechRenderer.components,
    day: AttendeeTechCommonRenderer,
    week: AttendeeTechCommonRenderer,
    month: AttendeeTechCommonRenderer,
    year: AttendeeTechYearRenderer,
};
