/** @odoo-module **/

import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { TecCalendarController } from "@tec/views/tec_calendar/tec_calendar_controller";
import { TecControlPanel } from "@tec/components/tec_control_panel/tec_control_panel";

export const tecCalendarView = {
    ...calendarView,
    Controller: TecCalendarController,
    ControlPanel: TecControlPanel,
};
registry.category("views").add("tec_calendar", tecCalendarView);
