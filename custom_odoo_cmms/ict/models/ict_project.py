# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import json
from pytz import UTC
from collections import defaultdict
from datetime import timedelta, datetime, time
from random import randint

from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt
from odoo.addons.rating.models import rating_data
from odoo.addons.web_editor.controllers.main import handle_history_divergence
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools.misc import get_lang

from .ict_project_task_recurrence import DAYS, WEEKS


class IctProject(models.Model):
    _name = 'ict.project.task'
    _description = 'ICT Task'

    recurring_task = fields.Boolean(string="Recurrent")
    recurring_count = fields.Integer(string="Tasks in Recurrence", compute='_compute_recurring_count')# Copy Compute 1
    recurrence_id = fields.Many2one('ict.project.task.recurrence', copy=False)
    recurrence_update = fields.Selection([
        ('this', 'This task'),
        ('subsequent', 'This and following tasks'),
        ('all', 'All tasks'),
    ], default='this', store=False)
    recurrence_message = fields.Char(string='Next Recurrencies', compute='_compute_recurrence_message',# Copy Compute 2
                                     groups="project.group_ict_project_user")

    repeat_interval = fields.Integer(string='Repeat Every', default=1, compute='_compute_repeat', readonly=False,# Copy Compute 3 Continue from HERE
                                     groups="project.group_ict_project_user")
    repeat_unit = fields.Selection([
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months'),
        ('year', 'Years'),
    ], default='week', compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    repeat_type = fields.Selection([
        ('forever', 'Forever'),
        ('until', 'End Date'),
        ('after', 'Number of Repetitions'),
    ], default="forever", string="Until", compute='_compute_repeat', readonly=False,
        groups="project.group_project_user")
    repeat_until = fields.Date(string="End Date", compute='_compute_repeat', readonly=False,
                               groups="project.group_project_user")
    repeat_number = fields.Integer(string="Repetitions", default=1, compute='_compute_repeat', readonly=False,
                                   groups="project.group_project_user")

    repeat_on_month = fields.Selection([
        ('date', 'Date of the Month'),
        ('day', 'Day of the Month'),
    ], default='date', compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_on_year = fields.Selection([
        ('date', 'Date of the Year'),
        ('day', 'Day of the Year'),
    ], default='date', compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    mon = fields.Boolean(string="Mon", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    tue = fields.Boolean(string="Tue", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    wed = fields.Boolean(string="Wed", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    thu = fields.Boolean(string="Thu", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    fri = fields.Boolean(string="Fri", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    sat = fields.Boolean(string="Sat", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    sun = fields.Boolean(string="Sun", compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_day = fields.Selection([
        (str(i), str(i)) for i in range(1, 32)
    ], compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    repeat_week = fields.Selection([
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
        ('last', 'Last'),
    ], default='first', compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    repeat_weekday = fields.Selection([
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ], string='Day Of The Week', compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    repeat_month = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December'),
    ], compute='_compute_repeat', readonly=False, groups="project.group_project_user")

    repeat_show_dow = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")
    repeat_show_day = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")
    repeat_show_week = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")
    repeat_show_month = fields.Boolean(compute='_compute_repeat_visibility', groups="project.group_project_user")

    @api.depends('recurrence_id')
    def _compute_recurring_count(self):# Copy Compute 1
         self.recurring_count = 0
         recurring_tasks = self.filtered(lambda l: l.recurrence_id)
         count = self.env['project.task']._read_group([('recurrence_id', 'in', recurring_tasks.recurrence_id.ids)],
                                                      ['id'], 'recurrence_id')
         tasks_count = {c.get('recurrence_id')[0]: c.get('recurrence_id_count') for c in count}
         for task in recurring_tasks:
              task.recurring_count = tasks_count.get(task.recurrence_id.id, 0)

    @api.depends(
        'recurring_task', 'repeat_interval', 'repeat_unit', 'repeat_type', 'repeat_until',
        'repeat_number', 'repeat_on_month', 'repeat_on_year', 'mon', 'tue', 'wed', 'thu', 'fri',
        'sat', 'sun', 'repeat_day', 'repeat_week', 'repeat_month', 'repeat_weekday')
    def _compute_recurrence_message(self):
        self.recurrence_message = False
        for task in self.filtered(lambda t: t.recurring_task and t._is_recurrence_valid()):
            date = task._get_recurrence_start_date()
            recurrence_left = task.recurrence_id.recurrence_left if task.recurrence_id else task.repeat_number
            number_occurrences = min(5, recurrence_left if task.repeat_type == 'after' else 5)
            delta = task.repeat_interval if task.repeat_unit == 'day' else 1
            recurring_dates = self.env['ict.project.task.recurrence']._get_next_recurring_dates(
                date + timedelta(days=delta),
                task.repeat_interval,
                task.repeat_unit,
                task.repeat_type,
                task.repeat_until,
                task.repeat_on_month,
                task.repeat_on_year,
                task._get_weekdays(WEEKS.get(task.repeat_week)),
                task.repeat_day,
                task.repeat_week,
                task.repeat_month,
                count=number_occurrences)
            date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format or get_lang(
                self.env).date_format
            if recurrence_left == 0:
                recurrence_title = _('There are no more occurrences.')
            else:
                recurrence_title = _('A new task will be created on the following dates:')
            task.recurrence_message = '<p><span class="fa fa-check-circle"></span> %s</p><ul>' % recurrence_title
            task.recurrence_message += ''.join(
                ['<li>%s</li>' % date.strftime(date_format) for date in recurring_dates[:5]])
            if task.repeat_type == 'after' and recurrence_left > 5 or task.repeat_type == 'forever' or len(
                    recurring_dates) > 5:
                task.recurrence_message += '<li>...</li>'
            task.recurrence_message += '</ul>'
            if task.repeat_type == 'until':
                task.recurrence_message += _('<p><em>Number of tasks: %(tasks_count)s</em></p>') % {
                    'tasks_count': len(recurring_dates)}

    @api.depends('recurring_task')
    def _compute_repeat(self):
        rec_fields = self._get_recurrence_fields()
        defaults = self.default_get(rec_fields)
        for task in self:
            for f in rec_fields:
                if task.recurrence_id:
                    task[f] = task.recurrence_id[f]
                else:
                    if task.recurring_task:
                        task[f] = defaults.get(f)
                    else:
                        task[f] = False