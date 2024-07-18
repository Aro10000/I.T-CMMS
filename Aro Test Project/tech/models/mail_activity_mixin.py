# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class MailActivityMixin(models.AbstractModel):
    _inherit = 'mail.activity.mixin'

    activity_tech_event_id = fields.Many2one(
        'tech.event', string="Next Activity Tech Event",
        compute='_compute_activity_tech_event_id', groups="base.group_user")

    @api.depends('activity_ids.tech_event_id')
    def _compute_activity_tech_event_id(self):
        """This computes the tech event of the next activity.
        It evaluates to false if there is no such event."""
        for record in self:
            record.activity_tech_event_id = fields.first(record.activity_ids).tech_event_id
