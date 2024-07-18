# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    meeting_count = fields.Integer("# Meetings", compute='_compute_meeting_count')
    meeting_ids = fields.Many2many('tech.event', 'tech_event_res_partner_rel', 'res_partner_id',
                                   'tech_event_id', string='Meetings', copy=False)

    tech_last_notif_ack = fields.Datetime(
        'Last notification marked as read from base Tech', default=fields.Datetime.now)

    def _compute_meeting_count(self):
        result = self._compute_meeting()
        for p in self:
            p.meeting_count = len(result.get(p.id, []))

    def _compute_meeting(self):
        if self.ids:
            all_partners = self.with_context(active_test=False).search_read([('id', 'child_of', self.ids)], ["parent_id"])
            all_partners_parents = {p["id"]: p['parent_id'][0] for p in all_partners if p.get('parent_id')}

            event_id = self.env['tech.event']._search([])  # ir.rules will be applied
            subquery_string, subquery_params = event_id.select()
            subquery = self.env.cr.mogrify(subquery_string, subquery_params).decode()

            self.env.cr.execute("""
                SELECT res_partner_id, tech_event_id, count(1)
                  FROM tech_event_res_partner_rel
                 WHERE res_partner_id IN %s AND tech_event_id IN ({})
              GROUP BY res_partner_id, tech_event_id
            """.format(subquery), [tuple(p["id"] for p in all_partners)])

            meeting_data = self.env.cr.fetchall()

            # Create a dict {partner_id: event_ids} and fill with events linked to the partner
            meetings = {}
            for p_id, m_id, _ in meeting_data:
                meetings.setdefault(p_id, set()).add(m_id)

            # Add the events linked to the children of the partner
            for meeting_pid in set(meetings):
                partner_id = meeting_pid
                while partner_id in all_partners_parents:
                    partner_id = all_partners_parents[partner_id]
                    if partner_id in self.ids:
                        meetings[partner_id] = meetings.get(partner_id, set()) | meetings[meeting_pid]
            return {p_id: list(meetings.get(p_id, set())) for p_id in self.ids}
        return {}

    def get_attendez_detail(self, meeting_ids):
        """ Return a list of dict of the given meetings with the attendezs details
            Used by:
                - base_tech.js : Many2ManyAttendez
                - tech_model.js (tech.TechModel)
        """
        attendezs_details = []
        meetings = self.env['tech.event'].browse(meeting_ids)
        for attendez in meetings.attendez_ids:
            if attendez.partner_id not in self:
                continue
            attendez_is_organizer = self.env.user == attendez.event_id.user_id and attendez.partner_id == self.env.user.partner_id
            attendezs_details.append({
                'id': attendez.partner_id.id,
                'name': attendez.partner_id.display_name,
                'status': attendez.state,
                'event_id': attendez.event_id.id,
                'attendez_id': attendez.id,
                'is_alone': attendez.event_id.is_organizer_alone and attendez_is_organizer,
                # attendezs data is sorted according to this key in JS.
                'is_organizer': 1 if attendez.partner_id == attendez.event_id.user_id.partner_id else 0,
            })
        return attendezs_details

    @api.model
    def _set_tech_last_notif_ack(self):
        partner = self.env['res.users'].browse(self.env.context.get('uid', self.env.uid)).partner_id
        partner.write({'tech_last_notif_ack': datetime.now()})

    def schedule_meeting(self):
        self.ensure_one()
        partner_ids = self.ids
        partner_ids.append(self.env.user.partner_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("tech.action_tech_event")
        action['context'] = {
            'default_partner_ids': partner_ids,
        }
        action['domain'] = ['|', ('id', 'in', self._compute_meeting()[self.id]), ('partner_ids', 'in', self.ids)]
        return action
