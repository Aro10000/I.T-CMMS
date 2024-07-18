# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import formatLang

STATUS_COLOR = {
    'on_track': 20,  # green / success
    'at_risk': 2,  # orange
    'off_track': 23,  # red / danger
    'on_hold': 4,  # light blue
    False: 0,  # default grey -- for studio
    # Only used in tec.task
    'to_define': 0,
}

class TecUpdate(models.Model):
    _name = 'tec.update'
    _description = 'Tec Update'
    _order = 'date desc'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    def default_get(self, fields):
        result = super().default_get(fields)
        if 'tec_id' in fields and not result.get('tec_id'):
            result['tec_id'] = self.env.context.get('active_id')
        if result.get('tec_id'):
            tec = self.env['tec.tec'].browse(result['tec_id'])
            if 'progress' in fields and not result.get('progress'):
                result['progress'] = tec.last_update_id.progress
            if 'description' in fields and not result.get('description'):
                result['description'] = self._build_description(tec)
            if 'status' in fields and not result.get('status'):
                # `to_define` is not an option for self.status, here we actually want to default to `on_track`
                # the goal of `to_define` is for a tec to start without an actual status.
                result['status'] = tec.last_update_status if tec.last_update_status != 'to_define' else 'on_track'
        return result

    name = fields.Char("Title", required=True, tracking=True)
    status = fields.Selection(selection=[
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track'),
        ('on_hold', 'On Hold')
    ], required=True, tracking=True)
    color = fields.Integer(compute='_compute_color')
    progress = fields.Integer(tracking=True)
    progress_percentage = fields.Float(compute='_compute_progress_percentage')
    user_id = fields.Many2one('res.users', string='Author', required=True, default=lambda self: self.env.user)
    description = fields.Html()
    date = fields.Date(default=fields.Date.context_today, tracking=True)
    tec_id = fields.Many2one('tec.tec', required=True)
    name_cropped = fields.Char(compute="_compute_name_cropped")

    @api.depends('status')
    def _compute_color(self):
        for update in self:
            update.color = STATUS_COLOR[update.status]

    @api.depends('progress')
    def _compute_progress_percentage(self):
        for u in self:
            u.progress_percentage = u.progress / 100

    @api.depends('name')
    def _compute_name_cropped(self):
        for u in self:
            u.name_cropped = (u.name[:57] + '...') if len(u.name) > 60 else u.name

    # ---------------------------------
    # ORM Override
    # ---------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        updates = super().create(vals_list)
        for update in updates:
            update.tec_id.sudo().last_update_id = update
        return updates

    def unlink(self):
        tecs = self.tec_id
        res = super().unlink()
        for tec in tecs:
            tec.last_update_id = self.search([('tec_id', "=", tec.id)], order="date desc", limit=1)
        return res

    # ---------------------------------
    # Build default description
    # ---------------------------------
    @api.model
    def _build_description(self, tec):
        return self.env['ir.qweb']._render('tec.tec_update_default_description', self._get_template_values(tec))

    @api.model
    def _get_template_values(self, tec):
        milestones = self._get_milestone_values(tec)
        return {
            'user': self.env.user,
            'tec': tec,
            'show_activities': milestones['show_section'],
            'milestones': milestones,
            'format_lang': lambda value, digits: formatLang(self.env, value, digits=digits),
        }

    @api.model
    def _get_milestone_values(self, tec):
        Milestone = self.env['tec.milestone']
        if not tec.allow_milestones:
            return {
                'show_section': False,
                'list': [],
                'updated': [],
                'last_update_date': None,
                'created': []
            }
        list_milestones = Milestone.search(
            [('tec_id', '=', tec.id),
             '|', ('deadline', '<', fields.Date.context_today(self) + relativedelta(years=1)), ('deadline', '=', False)])._get_data_list()
        updated_milestones = self._get_last_updated_milestone(tec)
        domain = [('tec_id', '=', tec.id)]
        if tec.last_update_id.create_date:
            domain = expression.AND([domain, [('create_date', '>', tec.last_update_id.create_date)]])
        created_milestones = Milestone.search(domain)._get_data_list()
        return {
            'show_section': (list_milestones or updated_milestones or created_milestones) and True or False,
            'list': list_milestones,
            'updated': updated_milestones,
            'last_update_date': tec.last_update_id.create_date or None,
            'created': created_milestones,
        }

    @api.model
    def _get_last_updated_milestone(self, tec):
        query = """
            SELECT DISTINCT pm.id as milestone_id,
                            pm.deadline as deadline,
                            FIRST_VALUE(old_value_datetime::date) OVER w_partition as old_value,
                            pm.deadline as new_value
                       FROM mail_message mm
                 INNER JOIN mail_tracking_value mtv
                         ON mm.id = mtv.mail_message_id
                 INNER JOIN ir_model_fields imf
                         ON mtv.field = imf.id
                        AND imf.model = 'tec.milestone'
                        AND imf.name = 'deadline'
                 INNER JOIN tec_milestone pm
                         ON mm.res_id = pm.id
                      WHERE mm.model = 'tec.milestone'
                        AND mm.message_type = 'notification'
                        AND pm.tec_id = %(tec_id)s
         """
        if tec.last_update_id.create_date:
            query = query + "AND mm.date > %(last_update_date)s"
        query = query + """
                     WINDOW w_partition AS (
                             PARTITION BY pm.id
                             ORDER BY mm.date ASC
                            )
                   ORDER BY pm.deadline ASC
                   LIMIT 1;
        """
        query_params = {'tec_id': tec.id}
        if tec.last_update_id.create_date:
            query_params['last_update_date'] = tec.last_update_id.create_date
        self.env.cr.execute(query, query_params)
        results = self.env.cr.dictfetchall()
        mapped_result = {res['milestone_id']: {'new_value': res['new_value'], 'old_value': res['old_value']} for res in results}
        milestones = self.env['tec.milestone'].search([('id', 'in', list(mapped_result.keys()))])
        return [{
            **milestone._get_data(),
            'new_value': mapped_result[milestone.id]['new_value'],
            'old_value': mapped_result[milestone.id]['old_value'],
        } for milestone in milestones]
