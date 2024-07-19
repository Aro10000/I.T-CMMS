# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval


class TecTaskTypeDelete(models.TransientModel):
    _name = 'tec.task.type.delete.wizard'
    _description = 'Tec Stage Delete Wizard'

    tec_ids = fields.Many2many('tec.tec', domain="['|', ('active', '=', False), ('active', '=', True)]", string='Tecs', ondelete='cascade')
    stage_ids = fields.Many2many('tec.task.type', string='Stages To Delete', ondelete='cascade')
    tasks_count = fields.Integer('Number of Tasks', compute='_compute_tasks_count')
    stages_active = fields.Boolean(compute='_compute_stages_active')

    @api.depends('tec_ids')
    def _compute_tasks_count(self):
        for wizard in self:
            wizard.tasks_count = self.with_context(active_test=False).env['tec.task'].search_count([('stage_id', 'in', wizard.stage_ids.ids)])

    @api.depends('stage_ids')
    def _compute_stages_active(self):
        for wizard in self:
            wizard.stages_active = all(wizard.stage_ids.mapped('active'))

    def action_archive(self):
        if len(self.tec_ids) <= 1:
            return self.action_confirm()

        return {
            'name': _('Confirmation'),
            'view_mode': 'form',
            'res_model': 'tec.task.type.delete.wizard',
            'views': [(self.env.ref('tec.view_tec_task_type_delete_confirmation_wizard').id, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_unarchive_task(self):
        inactive_tasks = self.env['tec.task'].with_context(active_test=False).search(
            [('active', '=', False), ('stage_id', 'in', self.stage_ids.ids)])
        inactive_tasks.action_unarchive()

    def action_confirm(self):
        tasks = self.with_context(active_test=False).env['tec.task'].search([('stage_id', 'in', self.stage_ids.ids)])
        tasks.write({'active': False})
        self.stage_ids.write({'active': False})
        return self._get_action()

    def action_unlink(self):
        self.stage_ids.unlink()
        return self._get_action()

    def _get_action(self):
        tec_id = self.env.context.get('default_tec_id')

        if tec_id:
            action = self.env["ir.actions.actions"]._for_xml_id("tec.action_view_task")
            action['domain'] = [('tec_id', '=', tec_id)]
            action['context'] = str({
                'pivot_row_groupby': ['user_ids'],
                'default_tec_id': tec_id,
            })
        elif self.env.context.get('stage_view'):
            action = self.env["ir.actions.actions"]._for_xml_id("tec.open_task_type_form")
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("tec.action_view_all_task")

        context = action.get('context', '{}')
        context = context.replace('uid', str(self.env.uid))
        context = dict(literal_eval(context), active_test=True)
        action['context'] = context
        action['target'] = 'main'
        return action
