/** @odoo-module **/

import { ControlPanel } from "@web/search/control_panel/control_panel";
import { useService } from "@web/core/utils/hooks";

const { onWillStart } = owl;

export class TecControlPanel extends ControlPanel {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.user = useService("user");
        const { active_id, show_tec_update } = this.env.searchModel.globalContext;
        this.showTecUpdate = this.env.config.viewType === "form" || show_tec_update;
        this.tecId = this.showTecUpdate ? active_id : false;

        onWillStart(async () => {
            if (this.showTecUpdate) {
                await this.loadData();
            }
        });
    }

    async loadData() {
        const [data, isTecUser] = await Promise.all([
            this.orm.call("tec.tec", "get_last_update_or_default", [this.tecId]),
            this.user.hasGroup("tec.group_tec_user"),
        ]);
        this.data = data;
        this.isTecUser = isTecUser;
    }

    async onStatusClick(ev) {
        ev.preventDefault();
        this.actionService.doAction("tec.tec_update_all_action", {
            additionalContext: {
                default_tec_id: this.tecId,
                active_id: this.tecId,
            },
        });
    }
}

TecControlPanel.template = "tec.TecControlPanel";
