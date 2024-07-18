# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_tec_forecast = fields.Boolean(string="Planning")
    module_hr_timesheet = fields.Boolean(string="Task Logs")
    group_subtask_tec = fields.Boolean("Sub-tasks", implied_group="tec.group_subtask_tec")
    group_tec_rating = fields.Boolean("Customer Ratings", implied_group='tec.group_tec_rating')
    group_tec_stages = fields.Boolean("Tec Stages", implied_group="tec.group_tec_stages")
    group_tec_recurring_tasks = fields.Boolean("Recurring Tasks", implied_group="tec.group_tec_recurring_tasks")
    group_tec_task_dependencies = fields.Boolean("Task Dependencies", implied_group="tec.group_tec_task_dependencies")
    group_tec_milestone = fields.Boolean('Milestones', implied_group='tec.group_tec_milestone', group='base.group_portal,base.group_user')

    # Analytic Accounting
    analytic_plan_id = fields.Many2one(
        comodel_name='account.analytic.plan',
        string="Default Plan",
        readonly=False,
        related='company_id.analytic_plan_id',
    )

    @api.model
    def _get_basic_tec_domain(self):
        return []

    def set_values(self):
        # Ensure that settings on existing tecs match the above fields
        tecs = self.env["tec.tec"].search([])
        basic_tecs = tecs.filtered_domain(self._get_basic_tec_domain())

        features = {
            # key: (config_flag, is_global), value: tec_flag
            ("group_tec_rating", True): "rating_active",
            ("group_tec_recurring_tasks", True): "allow_recurring_tasks",
            ("group_subtask_tec", False): "allow_subtasks",
            ("group_tec_task_dependencies", False): "allow_task_dependencies",
            ("group_tec_milestone", False): "allow_milestones",
        }

        for (config_flag, is_global), tec_flag in features.items():
            config_flag_global = f"tec.{config_flag}"
            config_feature_enabled = self[config_flag]
            if self.user_has_groups(config_flag_global) != config_feature_enabled:
                if config_feature_enabled and not is_global:
                    basic_tecs[tec_flag] = config_feature_enabled
                else:
                    tecs[tec_flag] = config_feature_enabled

        # Hide the task dependency changes subtype when the dependency setting is disabled
        task_dep_change_subtype_id = self.env.ref('tec.mt_task_dependency_change')
        tec_task_dep_change_subtype_id = self.env.ref('tec.mt_tec_task_dependency_change')
        if task_dep_change_subtype_id.hidden != (not self['group_tec_task_dependencies']):
            task_dep_change_subtype_id.hidden = not self['group_tec_task_dependencies']
            tec_task_dep_change_subtype_id.hidden = not self['group_tec_task_dependencies']
        # Hide Tec Stage Changed mail subtype according to the settings
        tec_stage_change_mail_type = self.env.ref('tec.mt_tec_stage_change')
        if tec_stage_change_mail_type.hidden == self['group_tec_stages']:
            tec_stage_change_mail_type.hidden = not self['group_tec_stages']

        super().set_values()
