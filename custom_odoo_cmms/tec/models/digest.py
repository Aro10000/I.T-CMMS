# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_tec_task_opened = fields.Boolean('Open Tasks')
    kpi_tec_task_opened_value = fields.Integer(compute='_compute_tec_task_opened_value')

    def _compute_tec_task_opened_value(self):
        if not self.env.user.has_group('tec.group_tec_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            record.kpi_tec_task_opened_value = self.env['tec.task'].search_count([
                ('stage_id.fold', '=', False),
                ('create_date', '>=', start),
                ('create_date', '<', end),
                ('company_id', '=', company.id),
                ('display_tec_id', '!=', False),
            ])

    def _compute_kpis_actions(self, company, user):
        res = super(Digest, self)._compute_kpis_actions(company, user)
        res['kpi_tec_task_opened'] = 'tec.open_view_tec_all&menu_id=%s' % self.env.ref('tec.menu_main_pm').id
        return res
