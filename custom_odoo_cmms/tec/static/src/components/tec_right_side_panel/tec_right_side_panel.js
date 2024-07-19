/** @odoo-module */

import { useService } from '@web/core/utils/hooks';
import { formatFloat } from '@web/views/fields/formatters';
import { session } from '@web/session';
import { ViewButton } from '@web/views/view_button/view_button';
import { FormViewDialog } from '@web/views/view_dialogs/form_view_dialog';

import { TecRightSidePanelSection } from './components/tec_right_side_panel_section';
import { TecMilestone } from './components/tec_milestone';
import { TecProfitability } from './components/tec_profitability';

const { Component, onWillStart, useState } = owl;

export class TecRightSidePanel extends Component {
    setup() {
        this.orm = useService('orm');
        this.actionService = useService('action');
        this.dialog = useService('dialog');
        this.state = useState({
            data: {
                milestones: {
                    data: [],
                },
                profitability_items: {
                    costs: { data: [], total: { billed: 0.0, to_bill: 0.0 } },
                    revenues: { data: [], total: { invoiced: 0.0, to_invoice: 0.0 } },
                },
                user: {},
                currency_id: false,
            }
        });

        onWillStart(() => this.loadData());
    }

    get context() {
        return this.props.context;
    }

    get domain() {
        return this.props.domain;
    }

    get tecId() {
        return this.context.active_id;
    }

    get currencyId() {
        return this.state.data.currency_id;
    }

    get sectionNames() {
        return {
            'milestones': this.env._t('Milestones'),
            'profitability': this.env._t('Profitability'),
        };
    }

    get showTecProfitability() {
        return !!this.state.data.profitability_items
            && (
                this.state.data.profitability_items.revenues.data.length > 0
                || this.state.data.profitability_items.costs.data.length > 0
            );
    }

    formatFloat(value) {
        return formatFloat(value, { digits: [false, 1] });
    }

    formatMonetary(value, options = {}) {
        const valueFormatted = formatFloat(value, {
            ...options,
            'digits': [false, 0],
            'noSymbol': true,
        });
        const currency = session.currencies[this.currencyId];
        if (!currency) {
            return valueFormatted;
        }
        if (currency.position === "after") {
            return `${valueFormatted}\u00A0${currency.symbol}`;
        } else {
            return `${currency.symbol}\u00A0${valueFormatted}`;
        }
    }

    async loadData() {
        if (!this.tecId) { // If this is called from notif, multiples updates but no specific tec
            return {};
        }
        const data = await this.orm.call(
            'tec.tec',
            'get_panel_data',
            [[this.tecId]],
            { context: this.context },
        );
        this.state.data = data;
        return data;
    }

    async loadMilestones() {
        const milestones = await this.orm.call(
            'tec.tec',
            'get_milestones',
            [[this.tecId]],
            { context: this.context },
        );
        this.state.data.milestones = milestones;
        return milestones;
    }

    addMilestone() {
        const context = {
            ...this.context,
            'default_tec_id': this.tecId,
        };
        this.openFormViewDialog({
            context,
            title: this.env._t('New Milestone'),
            resModel: 'tec.milestone',
            onRecordSaved: async () => {
                await this.loadMilestones();
            },
        });
    }

    async openFormViewDialog(params, options = {}) {
        this.dialog.add(FormViewDialog, params, options);
    }

    async onTecActionClick(params) {
        this.actionService.doActionButton({
            type: 'action',
            resId: this.tecId,
            context: this.context,
            resModel: 'tec.tec',
            ...params,
        });
    }

    _getStatButtonClickParams(statButton) {
        return {
            type: statButton.action_type,
            name: statButton.action,
            context: statButton.additional_context || '{}',
        };
    }

    _getStatButtonRecordParams() {
        return {
            resId: this.tecId,
            context: JSON.stringify(this.context),
            resModel: 'tec.tec',
        };
    }
}

TecRightSidePanel.components = { TecRightSidePanelSection, TecMilestone, ViewButton, TecProfitability };
TecRightSidePanel.template = 'tec.TecRightSidePanel';
TecRightSidePanel.props = {
    context: Object,
    domain: Array,
};
