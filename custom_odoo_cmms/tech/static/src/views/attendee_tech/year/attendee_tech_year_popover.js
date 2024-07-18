/** @odoo-module **/

import { TechYearPopover } from "@web/views/tech/tech_year/tech_year_popover";

export class AttendeeTechYearPopover extends TechYearPopover {
    getRecordClass(record) {
        const classes = [super.getRecordClass(record)];
        if (record.isAlone) {
            classes.push("o_attendee_status_alone");
        } else {
            classes.push(`o_attendee_status_${record.attendeeStatus}`);
        }
        return classes.join(" ");
    }
}
AttendeeTechYearPopover.subTemplates = {
    ...TechYearPopover.subTemplates,
    body: "tech.AttendeeTechYearPopover.body",
};
