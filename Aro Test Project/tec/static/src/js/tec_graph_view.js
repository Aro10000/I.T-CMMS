/** @odoo-module **/

import { TecControlPanel } from "@tec/components/tec_control_panel/tec_control_panel";
import { registry } from "@web/core/registry";
import { graphView } from "@web/views/graph/graph_view";

const viewRegistry = registry.category("views");

export const tecGraphView = {...graphView, ControlPanel: TecControlPanel};

viewRegistry.add("tec_graph", tecGraphView);
