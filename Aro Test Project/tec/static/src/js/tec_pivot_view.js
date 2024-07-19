/** @odoo-module **/

import { TecControlPanel } from "@tec/components/tec_control_panel/tec_control_panel";
import { registry } from "@web/core/registry";
import { pivotView } from "@web/views/pivot/pivot_view";

const tecPivotView = {...pivotView, ControlPanel: TecControlPanel};

registry.category("views").add("tec_pivot", tecPivotView);
