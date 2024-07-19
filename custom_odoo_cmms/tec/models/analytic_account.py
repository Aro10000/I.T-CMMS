# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    tec_ids = fields.One2many('tec.tec', 'analytic_account_id', string='Tecs')
    tec_count = fields.Integer("Tec Count", compute='_compute_tec_count')

    @api.depends('tec_ids')
    def _compute_tec_count(self):
        tec_data = self.env['tec.tec']._read_group([('analytic_account_id', 'in', self.ids)], ['analytic_account_id'], ['analytic_account_id'])
        mapping = {m['analytic_account_id'][0]: m['analytic_account_id_count'] for m in tec_data}
        for account in self:
            account.tec_count = mapping.get(account.id, 0)

    @api.constrains('company_id')
    def _check_company_id(self):
        for record in self:
            if record.company_id and not all(record.company_id == c for c in record.tec_ids.mapped('company_id')):
                raise UserError(_('You cannot change the company of an analytic account if it is related to a tec.'))

    @api.ondelete(at_uninstall=False)
    def _unlink_except_existing_tasks(self):
        tecs = self.env['tec.tec'].search([('analytic_account_id', 'in', self.ids)])
        has_tasks = self.env['tec.task'].search_count([('tec_id', 'in', tecs.ids)])
        if has_tasks:
            raise UserError(_('Please remove existing tasks in the tec linked to the accounts you want to delete.'))

    def action_view_tecs(self):
        kanban_view_id = self.env.ref('tec.view_tec_kanban').id
        result = {
            "type": "ir.actions.act_window",
            "res_model": "tec.tec",
            "views": [[kanban_view_id, "kanban"], [False, "form"]],
            "domain": [['analytic_account_id', '=', self.id]],
            "context": {"create": False},
            "name": _("Tecs"),
        }
        if len(self.tec_ids) == 1:
            result['views'] = [(False, "form")]
            result['res_id'] = self.tec_ids.id
        return result
