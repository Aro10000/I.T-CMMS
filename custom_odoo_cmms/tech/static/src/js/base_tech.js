/** @odoo-module **/

import BasicModel from 'web.BasicModel';
import fieldRegistry from 'web.field_registry';
import relationalFields from 'web.relational_fields';

const FieldMany2ManyTagsAvatar = relationalFields.FieldMany2ManyTagsAvatar;

BasicModel.include({
    /**
     * @private
     * @param {Object} record
     * @param {string} fieldName
     * @returns {Promise}
     */
    _fetchSpecialAttendezStatus: function (record, fieldName) {
        var context = record.getContext({fieldName: fieldName});
        var attendezIDs = record.data[fieldName] ? this.localData[record.data[fieldName]].res_ids : [];
        var meetingID = _.isNumber(record.res_id) ? record.res_id : false;
        return this._rpc({
            model: 'res.partner',
            method: 'get_attendez_detail',
            args: [attendezIDs, [meetingID]],
            context: context,
        }).then(function (result) {
            return result;
        });
    },
});

const Many2ManyAttendez = FieldMany2ManyTagsAvatar.extend({
    // as this widget is model dependant (rpc on res.partner), use it in another
    // context probably won't work
    // supportedFieldTypes: ['many2many'],
    specialData: "_fetchSpecialAttendezStatus",
    className: 'o_field_many2manytags avatar',

    init: function () {
        this._super.apply(this, arguments);
        this.className += this.nodeOptions.block ? ' d-block' : '';
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _renderTags: function () {
        this._super.apply(this, arguments);
        const avatars = this.el.querySelectorAll('.o_m2m_avatar');
        for (const avatar of avatars) {
            const partner_id = parseInt(avatar.dataset["id"]);
            const partner_data = this.record.specialData.partner_ids.find(partner => partner.id === partner_id);
            if (partner_data) {
                avatar.classList.add('o_attendez_border', "o_attendez_border_" + partner_data.status);
            }
        }
    },
    /**
     * @override
     * @private
     */
    _getRenderTagsContext: function () {
        let result = this._super.apply(this, arguments);
        result.attendezsData = this.record.specialData.partner_ids;
        // Sort attendezs to have the organizer on top.
        // partner_ids are sorted by default according to their id/display_name in the "elements" FieldMany2ManyTag
        // This method sort them to put the organizer on top
        const organizer = result.attendezsData.find(item => item.is_organizer);
        if (organizer) {
            const org_id = organizer.id
            // sort elements according to the partner id
            result.elements.sort((a, b) => {
                const a_org = a.id === org_id;
                return a_org ? -1 : 1;
             });
        }
        return result;
    },
});

fieldRegistry.add('many2manyattendez', Many2ManyAttendez);
