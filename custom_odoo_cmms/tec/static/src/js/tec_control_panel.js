/** @odoo-module **/

import ControlPanel from 'web.ControlPanel';
import session from 'web.session';

const { onWillStart, onWillUpdateProps } = owl;

export class TecControlPanel extends ControlPanel {

    setup() {
        super.setup();
        this.show_tec_update = this.props.view.type === "form" || this.props.action.context.show_tec_update;
        this.tec_id = this.show_tec_update ? this.props.action.context.active_id : false;

        onWillStart(() => this._loadWidgetData());
        onWillUpdateProps(() => this._loadWidgetData());
    }

    async _loadWidgetData() {
        if (this.show_tec_update) {
            this.data = await this.rpc({
                model: 'tec.tec',
                method: 'get_last_update_or_default',
                args: [this.tec_id],
            });
            this.is_tec_user = await session.user_has_group('tec.group_tec_user');
        }
    }

    async onStatusClick(ev) {
        ev.preventDefault();
        await this.trigger('do-action', {
            action: "tec.tec_update_all_action",
            options: {
                additional_context: {
                    default_tec_id: this.tec_id,
                    active_id: this.tec_id
                }
            }
        });
    }
}
