/** @odoo-module */

const { Component } = owl;

export class TecRightSidePanelSection extends Component { }

TecRightSidePanelSection.props = {
    name: { type: String, optional: true },
    header: { type: Boolean, optional: true },
    show: Boolean,
    showData: { type: Boolean, optional: true },
    slots: {
        type: Object,
        shape: {
            default: Object, // Content is not optional
            header: { type: Object, optional: true },
            title: { type: Object, optional: true },
        },
    },
};
TecRightSidePanelSection.defaultProps = {
    header: true,
    showData: true,
};

TecRightSidePanelSection.template = 'tec.TecRightSidePanelSection';
