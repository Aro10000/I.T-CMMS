


class Task(models.Model):
    _name = "project.task"
    _description = "Task"
    _date_name = "date_assign"
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']
    _mail_post_access = 'read'
    _order = "priority desc, sequence, id desc"
    _primary_email = 'email_from'
    _check_company_auto = True

    @api.model
    def _get_default_partner_id(self, project=None, parent=None):
        if parent and parent.partner_id:
            return parent.partner_id.id
        if project and project.partner_id:
            return project.partner_id.id
        return False

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _default_personal_stage_type_id(self):
        return self.env['project.task.type'].search([('user_id', '=', self.env.user.id)], limit=1).id

    @api.model
    def _default_company_id(self):
        if self._context.get('default_project_id'):
            return self.env['project.project'].browse(self._context['default_project_id']).company_id
        return self.env.company

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.model
    def _read_group_personal_stage_type_ids(self, stages, domain, order):
        return stages.search(['|', ('id', 'in', stages.ids), ('user_id', '=', self.env.user.id)])

    active = fields.Boolean(default=True)
    name = fields.Char(string='Title', tracking=True, required=True, index='trigram')
    description = fields.Html(string='Description', sanitize_attributes=False)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], default='0', index=True, string="Priority", tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    stage_id = fields.Many2one('project.task.type', string='Stage', compute='_compute_stage_id',
        store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
        default=_get_default_stage_id, group_expand='_read_group_stage_ids',
        domain="[('project_ids', '=', project_id)]", copy=False, task_dependency_tracking=True)
    tag_ids = fields.Many2many('project.tags', string='Tags',
        help="You can only see tags that are already present in your project. If you try creating a tag that is already existing in other projects, it won't generate any duplicates.")
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Status',
        copy=False, default='normal', required=True, compute='_compute_kanban_state', readonly=False, store=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', tracking=True, task_dependency_tracking=True)
    create_date = fields.Datetime("Created On", readonly=True)
    write_date = fields.Datetime("Last Updated On", readonly=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', copy=False, readonly=True,
        help="Date on which this task was last assigned (or unassigned). Based on this, you can get statistics on the time it usually takes to assign tasks.")
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True, task_dependency_tracking=True)

    date_last_stage_update = fields.Datetime(string='Last Stage Update',
        index=True,
        copy=False,
        readonly=True,
        help="Date on which the stage of your task has last been modified.\n"
            "Based on this information you can identify tasks that are stalling and get statistics on the time it usually takes to move tasks from one stage to another.")
    project_id = fields.Many2one('project.project', string='Project', recursive=True,
        compute='_compute_project_id', store=True, readonly=False, precompute=True,
        index=True, tracking=True, check_company=True, change_default=True)
    task_properties = fields.Properties('Properties', definition='project_id.task_properties_definition', copy=True)
    # Defines in which project the task will be displayed / taken into account in statistics.
    # Example: 1 task A with 1 subtask B in project P
    # A -> project_id=P, display_project_id=P
    # B -> project_id=P (to inherit from ACL/security rules), display_project_id=False
    display_project_id = fields.Many2one('project.project', index=True)
    planned_hours = fields.Float("Initially Planned Hours", tracking=True)
    subtask_planned_hours = fields.Float("Sub-tasks Planned Hours", compute='_compute_subtask_planned_hours',
        help="Sum of the hours allocated for all the sub-tasks (and their own sub-tasks) linked to this task. Usually less than or equal to the allocated hours of this task.")
    # Tracking of this field is done in the write function
    user_ids = fields.Many2many('res.users', relation='project_task_user_rel', column1='task_id', column2='user_id', string='Assignees', context={'active_test': False}, tracking=True)
    # User names displayed in project sharing views
    portal_user_names = fields.Char(compute='_compute_portal_user_names', compute_sudo=True, search='_search_portal_user_names')
    # Second Many2many containing the actual personal stage for the current user
    # See project_task_stage_personal.py for the model defininition
    personal_stage_type_ids = fields.Many2many('project.task.type', 'project_task_user_rel', column1='task_id', column2='stage_id',
        ondelete='restrict', group_expand='_read_group_personal_stage_type_ids', copy=False,
        domain="[('user_id', '=', user.id)]", depends=['user_ids'], string='Personal Stage')
    # Personal Stage computed from the user
    personal_stage_id = fields.Many2one('project.task.stage.personal', string='Personal Stage State', compute_sudo=False,
        compute='_compute_personal_stage_id', help="The current user's personal stage.")
    # This field is actually a related field on personal_stage_id.stage_id
    # However due to the fact that personal_stage_id is computed, the orm throws out errors
    # saying the field cannot be searched.
    personal_stage_type_id = fields.Many2one('project.task.type', string='Personal User Stage',
        compute='_compute_personal_stage_type_id', inverse='_inverse_personal_stage_type_id', store=False,
        search='_search_personal_stage_type_id', default=_default_personal_stage_type_id,
        help="The current user's personal task stage.")
    partner_id = fields.Many2one('res.partner',
        string='Customer', recursive=True, tracking=True,
        compute='_compute_partner_id', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_is_company = fields.Boolean(related='partner_id.is_company', readonly=True)
    commercial_partner_id = fields.Many2one(related='partner_id.commercial_partner_id')
    partner_email = fields.Char(
        compute='_compute_partner_email', inverse='_inverse_partner_email',
        string='Email', readonly=False, store=True, copy=False)
    partner_phone = fields.Char(
        compute='_compute_partner_phone', inverse='_inverse_partner_phone',
        string="Phone", readonly=False, store=True, copy=False)
    partner_city = fields.Char(related='partner_id.city', readonly=False)
    email_cc = fields.Char(help='Email addresses that were in the CC of the incoming emails from this task and that are not currently linked to an existing customer.')
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', compute='_compute_company_id', store=True, readonly=False,
        required=True, copy=True, default=_default_company_id)
    color = fields.Integer(string='Color Index')
    project_color = fields.Integer(related='project_id.color', string='Project Color')
    rating_active = fields.Boolean(string='Project Rating Status', related="project_id.rating_active")
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
        help="Attachments that don't come from a message.")
    # In the domain of displayed_image_id, we couln't use attachment_ids because a one2many is represented as a list of commands so we used res_model & res_id
    displayed_image_id = fields.Many2one('ir.attachment', domain="[('res_model', '=', 'project.task'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]", string='Cover Image')
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True)
    is_closed = fields.Boolean(related="stage_id.fold", string="Closing Stage", store=True, index=True, help="Folded in Kanban stages are closing stages.")
    parent_id = fields.Many2one('project.task', string='Parent Task', index=True)
    ancestor_id = fields.Many2one('project.task', string='Ancestor Task', compute='_compute_ancestor_id', index='btree_not_null', recursive=True, store=True)
    child_ids = fields.One2many('project.task', 'parent_id', string="Sub-tasks")
    child_text = fields.Char(compute="_compute_child_text")
    allow_subtasks = fields.Boolean(string="Allow Sub-tasks", related="project_id.allow_subtasks", readonly=True)
    subtask_count = fields.Integer("Sub-task Count", compute='_compute_subtask_count')
    email_from = fields.Char(string='Email From', help="These people will receive email.", index='trigram',
        compute='_compute_email_from', recursive=True, store=True, readonly=False, copy=False)
    project_privacy_visibility = fields.Selection(related='project_id.privacy_visibility', string="Project Visibility")
    # Computed field about working time elapsed between record creation and assignation/closing.
    working_hours_open = fields.Float(compute='_compute_elapsed', string='Working Hours to Assign', digits=(16, 2), store=True, group_operator="avg")
    working_hours_close = fields.Float(compute='_compute_elapsed', string='Working Hours to Close', digits=(16, 2), store=True, group_operator="avg")
    working_days_open = fields.Float(compute='_compute_elapsed', string='Working Days to Assign', store=True, group_operator="avg")
    working_days_close = fields.Float(compute='_compute_elapsed', string='Working Days to Close', store=True, group_operator="avg")
    # customer portal: include comment and incoming emails in communication history
    website_message_ids = fields.One2many(domain=lambda self: [('model', '=', self._name), ('message_type', 'in', ['email', 'comment'])])
    is_private = fields.Boolean(compute='_compute_is_private', search='_search_is_private')
    allow_milestones = fields.Boolean(related='project_id.allow_milestones')
    milestone_id = fields.Many2one(
        'project.milestone',
        'Milestone',
        domain="[('project_id', '=', project_id)]",
        compute='_compute_milestone_id',
        readonly=False,
        store=True,
        tracking=True,
        index='btree_not_null',
        help="Deliver your services automatically when a milestone is reached by linking it to a sales order item."
    )
    has_late_and_unreached_milestone = fields.Boolean(
        compute='_compute_has_late_and_unreached_milestone',
        search='_search_has_late_and_unreached_milestone',
    )

    # Task Dependencies fields
    allow_task_dependencies = fields.Boolean(related='project_id.allow_task_dependencies')
    # Tracking of this field is done in the write function
    depend_on_ids = fields.Many2many('project.task', relation="task_dependencies_rel", column1="task_id",
                                     column2="depends_on_id", string="Blocked By", tracking=True, copy=False,
                                     domain="[('project_id', '!=', False), ('id', '!=', id)]")
    dependent_ids = fields.Many2many('project.task', relation="task_dependencies_rel", column1="depends_on_id",
                                     column2="task_id", string="Block", copy=False,
                                     domain="[('project_id', '!=', False), ('id', '!=', id)]")
    dependent_tasks_count = fields.Integer(string="Dependent Tasks", compute='_compute_dependent_tasks_count')
    is_blocked = fields.Boolean(compute='_compute_is_blocked', store=True, recursive=True)

    # Project sharing fields
    display_parent_task_button = fields.Boolean(compute='_compute_display_parent_task_button', compute_sudo=True)

    # recurrence fields
    allow_recurring_tasks = fields.Boolean(related='project_id.allow_recurring_tasks')
    recurring_task = fields.Boolean(string="Recurrent")
    recurring_count = fields.Integer(string="Tasks in Recurrence", compute='_compute_recurring_count')
    recurrence_id = fields.Many2one('project.task.recurrence', copy=False)
    recurrence_update = fields.Selection([
        ('this', 'This task'),
        ('subsequent', 'This and following tasks'),
        ('all', 'All tasks'),
    ], default='this', store=False)
    recurrence_message = fields.Char(string='Next Recurrencies', compute='_compute_recurrence_message', groups="project.group_project_user")

    repeat_interval = fields.Integer(string='Repeat Every', default=1, compute='_compute_repeat', readonly=False, groups="project.group_project_user")
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
    ], default="forever", string="Until", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    repeat_until = fields.Date(string="End Date", compute='_compute_repeat', readonly=False, groups="project.group_project_user")
    repeat_number = fields.Integer(string="Repetitions", default=1, compute='_compute_repeat', readonly=False, groups="project.group_project_user")

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

    # Account analytic
    analytic_account_id = fields.Many2one('account.analytic.account', ondelete='set null', compute='_compute_analytic_account_id', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", check_company=True,
        help="Analytic account to which this task and its timesheets are linked.\n"
            "Track the costs and revenues of your task by setting its analytic account on your related documents (e.g. sales orders, invoices, purchase orders, vendor bills, expenses etc.).\n"
            "By default, the analytic account of the project is set. However, it can be changed on each task individually if necessary.")
    is_analytic_account_id_changed = fields.Boolean('Is Analytic Account Manually Changed', compute='_compute_is_analytic_account_id_changed', store=True)
    project_analytic_account_id = fields.Many2one('account.analytic.account', string='Project Analytic Account', related='project_id.analytic_account_id')

    @property
    def SELF_READABLE_FIELDS(self):
        return PROJECT_TASK_READABLE_FIELDS | self.SELF_WRITABLE_FIELDS

    @property
    def SELF_WRITABLE_FIELDS(self):
        return PROJECT_TASK_WRITABLE_FIELDS

    @api.depends('project_id.analytic_account_id')
    def _compute_analytic_account_id(self):
        self.env.remove_to_compute(self._fields['is_analytic_account_id_changed'], self)
        for task in self:
            if not task.is_analytic_account_id_changed:
                task.analytic_account_id = task.project_id.analytic_account_id

    @api.depends('analytic_account_id')
    def _compute_is_analytic_account_id_changed(self):
        for task in self:
            task.is_analytic_account_id_changed = task.project_id and task.analytic_account_id != task.project_id.analytic_account_id

    @api.depends('project_id', 'parent_id')
    def _compute_is_private(self):
        # Modify accordingly, this field is used to display the lock on the task's kanban card
        for task in self:
            task.is_private = not task.project_id and not task.parent_id

    def _search_is_private(self, operator, value):
        if not isinstance(value, bool):
            raise ValueError(_('Value should be True or False (not %s)'), value)
        if operator not in ['=', '!=']:
            raise NotImplementedError(_('Operation should be = or != (not %s)'), value)
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('project_id', '=', False)]
        else:
            return [('project_id', '!=', False)]

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == 'search' and  self.env.user.notification_type == 'email':
            for node in arch.xpath("//filter[@name='message_needaction']"):
                node.set('invisible', '1')
        return arch, view

    @api.depends('stage_id', 'project_id')
    def _compute_kanban_state(self):
        self.kanban_state = 'normal'

    @api.depends('parent_id.ancestor_id')
    def _compute_ancestor_id(self):
        for task in self:
            task.ancestor_id = task.parent_id.ancestor_id or task.parent_id

    @api.depends_context('uid')
    @api.depends('user_ids')
    def _compute_personal_stage_id(self):
        # An user may only access his own 'personal stage' and there can only be one pair (user, task_id)
        personal_stages = self.env['project.task.stage.personal'].search([('user_id', '=', self.env.uid), ('task_id', 'in', self.ids)])
        self.personal_stage_id = False
        for personal_stage in personal_stages:
            personal_stage.task_id.personal_stage_id = personal_stage

    @api.depends('personal_stage_id')
    def _compute_personal_stage_type_id(self):
        for task in self:
            task.personal_stage_type_id = task.personal_stage_id.stage_id

    def _inverse_personal_stage_type_id(self):
        for task in self:
            task.personal_stage_id.stage_id = task.personal_stage_type_id

    @api.model
    def _search_personal_stage_type_id(self, operator, value):
        return [('personal_stage_type_ids', operator, value)]

    @api.model
    def _get_default_personal_stage_create_vals(self, user_id):
        return [
            {'sequence': 1, 'name': _('Inbox'), 'user_id': user_id, 'fold': False},
            {'sequence': 2, 'name': _('Today'), 'user_id': user_id, 'fold': False},
            {'sequence': 3, 'name': _('This Week'), 'user_id': user_id, 'fold': False},
            {'sequence': 4, 'name': _('This Month'), 'user_id': user_id, 'fold': False},
            {'sequence': 5, 'name': _('Later'), 'user_id': user_id, 'fold': False},
            {'sequence': 6, 'name': _('Done'), 'user_id': user_id, 'fold': True},
            {'sequence': 7, 'name': _('Canceled'), 'user_id': user_id, 'fold': True},
        ]

    def _populate_missing_personal_stages(self):
        # Assign the default personal stage for those that are missing
        personal_stages_without_stage = self.env['project.task.stage.personal'].sudo().search([('task_id', 'in', self.ids), ('stage_id', '=', False)])
        if personal_stages_without_stage:
            user_ids = personal_stages_without_stage.user_id
            personal_stage_by_user = defaultdict(lambda: self.env['project.task.stage.personal'])
            for personal_stage in personal_stages_without_stage:
                personal_stage_by_user[personal_stage.user_id] |= personal_stage
            for user_id in user_ids:
                stage = self.env['project.task.type'].sudo().search([('user_id', '=', user_id.id)], limit=1)
                # In the case no stages have been found, we create the default stages for the user
                if not stage:
                    stages = self.env['project.task.type'].sudo().with_context(lang=user_id.partner_id.lang, default_project_ids=False).create(
                        self.with_context(lang=user_id.partner_id.lang)._get_default_personal_stage_create_vals(user_id.id)
                    )
                    stage = stages[0]
                personal_stage_by_user[user_id].sudo().write({'stage_id': stage.id})

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        """ Set task notification based on project notification preference if user follow the project"""
        if not subtype_ids:
            project_followers = self.project_id.message_follower_ids.filtered(lambda f: f.partner_id.id in partner_ids)
            for project_follower in project_followers:
                project_subtypes = project_follower.subtype_ids
                task_subtypes = (project_subtypes.mapped('parent_id') | project_subtypes.filtered(lambda sub: sub.internal or sub.default)).ids if project_subtypes else None
                partner_ids.remove(project_follower.partner_id.id)
                super().message_subscribe(project_follower.partner_id.ids, task_subtypes)
        return super().message_subscribe(partner_ids, subtype_ids)

    @api.constrains('depend_on_ids')
    def _check_no_cyclic_dependencies(self):
        if not self._check_m2m_recursion('depend_on_ids'):
            raise ValidationError(_("Two tasks cannot depend on each other."))

    @api.model
    def _get_recurrence_fields(self):
        return ['repeat_interval', 'repeat_unit', 'repeat_type', 'repeat_until', 'repeat_number',
                'repeat_on_month', 'repeat_on_year', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat',
                'sun', 'repeat_day', 'repeat_week', 'repeat_month', 'repeat_weekday']

    @api.depends('recurring_task', 'repeat_unit', 'repeat_on_month', 'repeat_on_year')
    def _compute_repeat_visibility(self):
        for task in self:
            task.repeat_show_day = task.recurring_task and (task.repeat_unit == 'month' and task.repeat_on_month == 'date') or (task.repeat_unit == 'year' and task.repeat_on_year == 'date')
            task.repeat_show_week = task.recurring_task and (task.repeat_unit == 'month' and task.repeat_on_month == 'day') or (task.repeat_unit == 'year' and task.repeat_on_year == 'day')
            task.repeat_show_dow = task.recurring_task and task.repeat_unit == 'week'
            task.repeat_show_month = task.recurring_task and task.repeat_unit == 'year'

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

    def _get_weekdays(self, n=1):
        self.ensure_one()
        if self.repeat_unit == 'week':
            return [fn(n) for day, fn in DAYS.items() if self[day]]
        return [DAYS.get(self.repeat_weekday)(n)]

    def _get_recurrence_start_date(self):
        return fields.Date.today()

    @api.depends(
        'recurring_task', 'repeat_interval', 'repeat_unit', 'repeat_type', 'repeat_until',
        'repeat_number', 'repeat_on_month', 'repeat_on_year', 'mon', 'tue', 'wed', 'thu', 'fri',
        'sat', 'sun', 'repeat_day', 'repeat_week', 'repeat_month', 'repeat_weekday')
    def _compute_recurrence_message(self):
        self.recurrence_message = False
        for task in self.filtered(lambda t: t.recurring_task and t._is_recurrence_valid()):
            date = task._get_recurrence_start_date()
            recurrence_left = task.recurrence_id.recurrence_left if task.recurrence_id  else task.repeat_number
            number_occurrences = min(5, recurrence_left if task.repeat_type == 'after' else 5)
            delta = task.repeat_interval if task.repeat_unit == 'day' else 1
            recurring_dates = self.env['project.task.recurrence']._get_next_recurring_dates(
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
            date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format or get_lang(self.env).date_format
            if recurrence_left == 0:
                recurrence_title = _('There are no more occurrences.')
            else:
                recurrence_title = _('A new task will be created on the following dates:')
            task.recurrence_message = '<p><span class="fa fa-check-circle"></span> %s</p><ul>' % recurrence_title
            task.recurrence_message += ''.join(['<li>%s</li>' % date.strftime(date_format) for date in recurring_dates[:5]])
            if task.repeat_type == 'after' and recurrence_left > 5 or task.repeat_type == 'forever' or len(recurring_dates) > 5:
                task.recurrence_message += '<li>...</li>'
            task.recurrence_message += '</ul>'
            if task.repeat_type == 'until':
                task.recurrence_message += _('<p><em>Number of tasks: %(tasks_count)s</em></p>') % {'tasks_count': len(recurring_dates)}

    def _is_recurrence_valid(self):
        self.ensure_one()
        return self.repeat_interval > 0 and\
                (not self.repeat_show_dow or self._get_weekdays()) and\
                (self.repeat_type != 'after' or self.repeat_number) and\
                (self.repeat_type != 'until' or self.repeat_until and self.repeat_until > fields.Date.today())

    @api.depends('recurrence_id')
    def _compute_recurring_count(self):
        self.recurring_count = 0
        recurring_tasks = self.filtered(lambda l: l.recurrence_id)
        count = self.env['project.task']._read_group([('recurrence_id', 'in', recurring_tasks.recurrence_id.ids)], ['id'], 'recurrence_id')
        tasks_count = {c.get('recurrence_id')[0]: c.get('recurrence_id_count') for c in count}
        for task in recurring_tasks:
            task.recurring_count = tasks_count.get(task.recurrence_id.id, 0)

    @api.depends('dependent_ids')
    def _compute_dependent_tasks_count(self):
        tasks_with_dependency = self.filtered('allow_task_dependencies')
        (self - tasks_with_dependency).dependent_tasks_count = 0
        if tasks_with_dependency:
            group_dependent = self.env['project.task']._read_group([
                ('depend_on_ids', 'in', tasks_with_dependency.ids),
            ], ['depend_on_ids'], ['depend_on_ids'])
            dependent_tasks_count_dict = {
                group['depend_on_ids'][0]: group['depend_on_ids_count']
                for group in group_dependent
            }
            for task in tasks_with_dependency:
                task.dependent_tasks_count = dependent_tasks_count_dict.get(task.id, 0)

    @api.depends('depend_on_ids.is_closed', 'depend_on_ids.is_blocked')
    def _compute_is_blocked(self):
        for task in self:
            task.is_blocked = any(not blocking_task.is_closed or blocking_task.is_blocked for blocking_task in task.depend_on_ids)

    @api.depends('partner_id.email')
    def _compute_partner_email(self):
        for task in self:
            if task.partner_id.email != task.partner_email:
                task.partner_email = task.partner_id.email

    def _inverse_partner_email(self):
        for task in self:
            if task.partner_id and task.partner_email != task.partner_id.email:
                task.partner_id.email = task.partner_email

    @api.depends('partner_id.phone')
    def _compute_partner_phone(self):
        for task in self:
            if task.partner_phone != task.partner_id.phone:
                task.partner_phone = task.partner_id.phone

    def _inverse_partner_phone(self):
        for task in self:
            if task.partner_id and task.partner_phone != task.partner_id.phone:
                task.partner_id.phone = task.partner_phone

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create a recursive hierarchy of tasks.'))

    def _get_attachments_search_domain(self):
        self.ensure_one()
        return [('res_id', '=', self.id), ('res_model', '=', 'project.task')]

    def _compute_attachment_ids(self):
        for task in self:
            attachment_ids = self.env['ir.attachment'].search(task._get_attachments_search_domain()).ids
            message_attachment_ids = task.mapped('message_ids.attachment_ids').ids  # from mail_thread
            task.attachment_ids = [(6, 0, list(set(attachment_ids) - set(message_attachment_ids)))]

    @api.depends('create_date', 'date_end', 'date_assign')
    def _compute_elapsed(self):
        task_linked_to_calendar = self.filtered(
            lambda task: task.project_id.resource_calendar_id and task.create_date
        )
        for task in task_linked_to_calendar:
            dt_create_date = fields.Datetime.from_string(task.create_date)

            if task.date_assign:
                dt_date_assign = fields.Datetime.from_string(task.date_assign)
                duration_data = task.project_id.resource_calendar_id.get_work_duration_data(dt_create_date, dt_date_assign, compute_leaves=True)
                task.working_hours_open = duration_data['hours']
                task.working_days_open = duration_data['days']
            else:
                task.working_hours_open = 0.0
                task.working_days_open = 0.0

            if task.date_end:
                dt_date_end = fields.Datetime.from_string(task.date_end)
                duration_data = task.project_id.resource_calendar_id.get_work_duration_data(dt_create_date, dt_date_end, compute_leaves=True)
                task.working_hours_close = duration_data['hours']
                task.working_days_close = duration_data['days']
            else:
                task.working_hours_close = 0.0
                task.working_days_close = 0.0

        (self - task_linked_to_calendar).update(dict.fromkeys(
            ['working_hours_open', 'working_hours_close', 'working_days_open', 'working_days_close'], 0.0))

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    def _compute_access_url(self):
        super(Task, self)._compute_access_url()
        for task in self:
            task.access_url = f'/my/tasks/{task.id}'

    def _compute_access_warning(self):
        super(Task, self)._compute_access_warning()
        for task in self.filtered(lambda x: x.project_id.privacy_visibility != 'portal'):
            task.access_warning = _(
                "The task cannot be shared with the recipient(s) because the privacy of the project is too restricted. Set the privacy of the project to 'Visible by following customers' in order to make it accessible by the recipient(s).")

    @api.depends('child_ids.planned_hours')
    def _compute_subtask_planned_hours(self):
        for task in self:
            task.subtask_planned_hours = sum(child_task.planned_hours + child_task.subtask_planned_hours for child_task in task.child_ids)

    @api.depends('child_ids')
    def _compute_child_text(self):
        for task in self:
            if not task.subtask_count:
                task.child_text = False
            elif task.subtask_count == 1:
                task.child_text = _("(+ 1 task)")
            else:
                task.child_text = _("(+ %(child_count)s tasks)", child_count=task.subtask_count)

    @api.depends('child_ids')
    def _compute_subtask_count(self):
        subtasks_per_task = self._get_subtask_ids_per_task_id()
        for task in self:
            task.subtask_count = len(subtasks_per_task.get(task.id, []))

    @api.onchange('company_id')
    def _onchange_task_company(self):
        if self.project_id.company_id != self.company_id:
            self.project_id = False

    @api.depends('project_id.company_id')
    def _compute_company_id(self):
        for task in self.filtered(lambda task: task.project_id):
            task.company_id = task.project_id.company_id

    @api.depends('project_id')
    def _compute_stage_id(self):
        for task in self:
            if task.project_id:
                if task.project_id not in task.stage_id.project_ids:
                    task.stage_id = task.stage_find(task.project_id.id, [('fold', '=', False)])
            else:
                task.stage_id = False

    @api.depends('user_ids')
    def _compute_portal_user_names(self):
        """ This compute method allows to see all the names of assigned users to each task contained in `self`.

            When we are in the project sharing feature, the `user_ids` contains only the users if we are a portal user.
            That is, only the users in the same company of the current user.
            So this compute method is a related of `user_ids.name` but with more records that the portal user
            can normally see.
            (In other words, this compute is only used in project sharing views to see all assignees for each task)
        """
        if self.ids:
            # fetch 'user_ids' in superuser mode (and override value in cache
            # browse is useful to avoid miscache because of the newIds contained in self
            self.invalidate_recordset(fnames=['user_ids'])
            self.browse(self.ids)._read(['user_ids'])
        for task in self.with_context(prefetch_fields=False):
            task.portal_user_names = ', '.join(task.user_ids.mapped('name'))

    def _search_portal_user_names(self, operator, value):
        if operator != 'ilike' and not isinstance(value, str):
            raise ValidationError(_('Not Implemented.'))

        query = """
            SELECT task_user.task_id
              FROM project_task_user_rel task_user
        INNER JOIN res_users users ON task_user.user_id = users.id
        INNER JOIN res_partner partners ON partners.id = users.partner_id
             WHERE partners.name ILIKE %s
        """
        return [('id', 'inselect', (query, [f'%{value}%']))]

    def _compute_display_parent_task_button(self):
        accessible_parent_tasks = self.parent_id.with_user(self.env.user)._filter_access_rules('read')
        for task in self:
            task.display_parent_task_button = task.parent_id in accessible_parent_tasks

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if self.allow_task_dependencies and 'task_mapping' not in self.env.context:
            self = self.with_context(task_mapping=dict())
        has_default_name = bool(default.get('name', ''))
        if not has_default_name:
            default['name'] = _("%s (copy)", self.name)
        if self.recurrence_id:
            default['recurrence_id'] = self.recurrence_id.copy().id
        if self.allow_subtasks:
            default_child_ids = []
            should_copy_stage_id = bool(default.get('stage_id', False))
            for child in self.child_ids:
                subtask_default = {}
                if has_default_name:
                    subtask_default['name'] = child.name
                if should_copy_stage_id:
                    subtask_default['stage_id'] = child.stage_id.id
                default_child_ids.append(child.copy(subtask_default).id)
            default['child_ids'] = default_child_ids
        task_copy = super(Task, self).copy(default)
        if self.allow_task_dependencies:
            task_mapping = self.env.context.get('task_mapping')
            task_mapping[self.id] = task_copy.id
            new_tasks = task_mapping.values()
            self.write({'depend_on_ids': [Command.unlink(t.id) for t in self.depend_on_ids if t.id in new_tasks]})
            self.write({'dependent_ids': [Command.unlink(t.id) for t in self.dependent_ids if t.id in new_tasks]})
            task_copy.write({'depend_on_ids': [Command.link(task_mapping.get(t.id, t.id)) for t in self.depend_on_ids]})
            task_copy.write({'dependent_ids': [Command.link(task_mapping.get(t.id, t.id)) for t in self.dependent_ids]})
        if self.allow_milestones:
            milestone_mapping = self.env.context.get('milestone_mapping', {})
            task_copy.milestone_id = milestone_mapping.get(task_copy.milestone_id.id, task_copy.milestone_id.id)
        return task_copy

    @api.model
    def get_empty_list_help(self, help):
        tname = _("task")
        project_id = self.env.context.get('default_project_id', False)
        if project_id:
            name = self.env['project.project'].browse(project_id).label_tasks
            if name: tname = name.lower()

        self = self.with_context(
            empty_list_help_id=self.env.context.get('default_project_id'),
            empty_list_help_model='project.project',
            empty_list_help_document_name=tname,
        )
        return super(Task, self).get_empty_list_help(help)

    def _valid_field_parameter(self, field, name):
        # If the field has `task_dependency_tracking` on we track the changes made in the dependent task on the parent task
        return name == 'task_dependency_tracking' or super()._valid_field_parameter(field, name)

    @tools.ormcache('self.env.uid', 'self.env.su')
    def _get_depends_tracked_fields(self):
        """ Returns the set of tracked field names for the current model.
        Those fields are the ones tracked in the parent task when using task dependencies.

        See :meth:`mail.models.MailThread._track_get_fields`"""
        fields = {name for name, field in self._fields.items() if getattr(field, 'task_dependency_tracking', None)}
        return fields and set(self.fields_get(fields))

    # ----------------------------------------
    # Case management
    # ----------------------------------------

    def stage_find(self, section_id, domain=[], order='sequence, id'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    # ------------------------------------------------
    # CRUD overrides
    # ------------------------------------------------
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields = super().fields_get(allfields=allfields, attributes=attributes)
        if not self.env.user.has_group('base.group_portal'):
            return fields
        readable_fields = self.SELF_READABLE_FIELDS
        public_fields = {field_name: description for field_name, description in fields.items() if field_name in readable_fields}

        writable_fields = self.SELF_WRITABLE_FIELDS
        for field_name, description in public_fields.items():
            if field_name not in writable_fields and not description.get('readonly', False):
                # If the field is not in Writable fields and it is not readonly then we force the readonly to True
                description['readonly'] = True

        return public_fields

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type='form', **options):
        """The override of fields_get making fields readonly for portal users
        makes the view cache dependent on the fact the user has the group portal or not

        The override of _get_view making the "Unread messages" filter invisible
        according to the user notification type
        makes the view cache dependent on the user notification type"""
        key = super()._get_view_cache_key(view_id, view_type, **options)
        key = key + (self.env.user.has_group('base.group_portal'),)
        if view_type == 'search':
            key += (self.env.user.notification_type,)
        return key

    @api.model
    def default_get(self, default_fields):
        vals = super(Task, self).default_get(default_fields)

        days = list(DAYS.keys())
        week_start = fields.Datetime.today().weekday()

        if all(d in default_fields for d in days):
            vals[days[week_start]] = True
        if 'repeat_day' in default_fields:
            vals['repeat_day'] = str(fields.Datetime.today().day)
        if 'repeat_month' in default_fields:
            vals['repeat_month'] = self._fields.get('repeat_month').selection[fields.Datetime.today().month - 1][0]
        if 'repeat_until' in default_fields:
            vals['repeat_until'] = fields.Date.today() + timedelta(days=7)
        if 'repeat_weekday' in default_fields:
            vals['repeat_weekday'] = self._fields.get('repeat_weekday').selection[week_start][0]

        if 'partner_id' in vals and not vals['partner_id']:
            # if the default_partner_id=False or no default_partner_id then we search the partner based on the project and parent
            project_id = vals.get('project_id')
            parent_id = vals.get('parent_id', self.env.context.get('default_parent_id'))
            if project_id or parent_id:
                partner_id = self._get_default_partner_id(
                    project_id and self.env['project.project'].browse(project_id),
                    parent_id and self.env['project.task'].browse(parent_id)
                )
                if partner_id:
                    vals['partner_id'] = partner_id
        project_id = vals.get('project_id', self.env.context.get('default_project_id'))
        if project_id:
            project = self.env['project.project'].browse(project_id)
            if project.analytic_account_id:
                vals['analytic_account_id'] = project.analytic_account_id.id
        elif 'default_user_ids' not in self.env.context:
            user_ids = vals.get('user_ids', [])
            user_ids.append(Command.link(self.env.user.id))
            vals['user_ids'] = user_ids

        return vals

    def _ensure_fields_are_accessible(self, fields, operation='read', check_group_user=True):
        """" ensure all fields are accessible by the current user

            This method checks if the portal user can access to all fields given in parameter.
            By default, it checks if the current user is a portal user and then checks if all fields are accessible for this user.

            :param fields: list of fields to check if the current user can access.
            :param operation: contains either 'read' to check readable fields or 'write' to check writable fields.
            :param check_group_user: contains boolean value.
                - True, if the method has to check if the current user is a portal one.
                - False if we are sure the user is a portal user,
        """
        assert operation in ('read', 'write'), 'Invalid operation'
        if fields and (not check_group_user or self.env.user.has_group('base.group_portal')) and not self.env.su:
            unauthorized_fields = set(fields) - (self.SELF_READABLE_FIELDS if operation == 'read' else self.SELF_WRITABLE_FIELDS)
            if unauthorized_fields:
                if operation == 'read':
                    error_message = _('You cannot read %s fields in task.', ', '.join(unauthorized_fields))
                else:
                    error_message = _('You cannot write on %s fields in task.', ', '.join(unauthorized_fields))
                raise AccessError(error_message)

    def _get_portal_sudo_vals(self, vals, defaults=False):
        """ returns the values which must be written without and with sudo when a portal user creates / writes a task.
            :param vals: dict of {field: value}, the values to create/write
            :return: a tuple with 2 dicts:
                - the first with the values to write without sudo
                - the second with the values to write with sudo
        """
        vals_no_sudo = {key: val for key, val in vals.items() if self._fields[key].type in ('one2many', 'many2many')}
        if defaults:
            vals_no_sudo.update({
                key[8:]: value
                for key, value in self.env.context.items()
                if key.startswith('default_') and key[8:] in self.SELF_WRITABLE_FIELDS and self._fields[key[8:]].type in ('one2many', 'many2many')
            })
        vals_sudo = {key: val for key, val in vals.items() if key not in vals_no_sudo}
        return vals_no_sudo, vals_sudo

    @api.model
    def _get_portal_sudo_context(self):
        return {
            key: value for key, value in self.env.context.items()
            if key == 'default_project_id'
            or key == 'default_user_ids' and value is False \
            or not key.startswith('default_')
            or key[8:] in (field for field in self.SELF_WRITABLE_FIELDS if self._fields[field].type not in ('one2many', 'many2many'))
        }

    def read(self, fields=None, load='_classic_read'):
        self._ensure_fields_are_accessible(fields)
        return super(Task, self).read(fields=fields, load=load)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        fields_list = ([f.split(':')[0] for f in fields] or [])
        if groupby:
            fields_groupby = [groupby] if isinstance(groupby, str) else groupby
            # only take field name when having ':' e.g 'date_deadline:week' => 'date_deadline'
            fields_list += [f.split(':')[0] for f in fields_groupby]
        if domain:
            fields_list += [term[0].split('.')[0] for term in domain if isinstance(term, (tuple, list)) and term not in [expression.TRUE_LEAF, expression.FALSE_LEAF]]
        self._ensure_fields_are_accessible(fields_list)
        return super(Task, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        fields_list = {term[0] for term in args if isinstance(term, (tuple, list)) and term not in [expression.TRUE_LEAF, expression.FALSE_LEAF]}
        self._ensure_fields_are_accessible(fields_list)
        return super(Task, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    def mapped(self, func):
        # Note: This will protect the filtered method too
        if func and isinstance(func, str):
            fields_list = func.split('.')
            self._ensure_fields_are_accessible(fields_list)
        return super(Task, self).mapped(func)

    def filtered_domain(self, domain):
        fields_list = [term[0] for term in domain if isinstance(term, (tuple, list)) and term not in [expression.TRUE_LEAF, expression.FALSE_LEAF]]
        self._ensure_fields_are_accessible(fields_list)
        return super(Task, self).filtered_domain(domain)

    def copy_data(self, default=None):
        defaults = super().copy_data(default=default)
        if self.env.user.has_group('project.group_project_user'):
            return defaults
        return [{k: v for k, v in default.items() if k in self.SELF_READABLE_FIELDS} for default in defaults]

    @api.model
    def _ensure_portal_user_can_write(self, fields):
        for field in fields:
            if field not in self.SELF_WRITABLE_FIELDS:
                raise AccessError(_('You have not write access of %s field.') % field)

    def _load_records_create(self, vals_list):
        projects_with_recurrence = self.env['project.project'].search([('allow_recurring_tasks', '=', True)])
        for vals in vals_list:
            if vals.get('recurring_task'):
                if vals.get('project_id') in projects_with_recurrence.ids and not vals.get('recurrence_id'):
                    default_val = self.default_get(self._get_recurrence_fields())
                    vals.update(**default_val)
                else:
                    for field_name in self._get_recurrence_fields() + ['recurring_task']:
                        vals.pop(field_name, None)
            project_id = vals.get('project_id')
            if project_id:
                self = self.with_context(default_project_id=project_id)
        tasks = super()._load_records_create(vals_list)
        stage_ids_per_project = defaultdict(list)
        for task in tasks:
            if task.stage_id and task.stage_id not in task.project_id.type_ids and task.stage_id.id not in stage_ids_per_project[task.project_id]:
                stage_ids_per_project[task.project_id].append(task.stage_id.id)

        for project, stage_ids in stage_ids_per_project.items():
            project.write({'type_ids': [Command.link(stage_id) for stage_id in stage_ids]})

        return tasks

    @api.model_create_multi
    def create(self, vals_list):
        is_portal_user = self.env.user.has_group('base.group_portal')
        if is_portal_user:
            self.check_access_rights('create')
        default_stage = dict()
        is_superuser = self._uid == SUPERUSER_ID
        for vals in vals_list:
            if is_portal_user:
                self._ensure_fields_are_accessible(vals.keys(), operation='write', check_group_user=False)

            project_id = vals.get('project_id') or self.env.context.get('default_project_id')
            if not vals.get('parent_id'):
                # 1) We must initialize display_project_id to follow project_id if there is no parent_id
                vals['display_project_id'] = project_id
            if project_id and not "company_id" in vals:
                vals["company_id"] = self.env["project.project"].browse(
                    project_id
                ).company_id.id or self.env.company.id
            if not project_id and ("stage_id" in vals or self.env.context.get('default_stage_id')):
                vals["stage_id"] = False

            if project_id and "stage_id" not in vals:
                # 1) Allows keeping the batch creation of tasks
                # 2) Ensure the defaults are correct (and computed once by project),
                # by using default get (instead of _get_default_stage_id or _stage_find),
                if project_id not in default_stage:
                    default_stage[project_id] = self.with_context(
                        default_project_id=project_id
                    ).default_get(['stage_id']).get('stage_id')
                vals["stage_id"] = default_stage[project_id]
            # user_ids change: update date_assign
            if vals.get('user_ids'):
                vals['date_assign'] = fields.Datetime.now()
                if not project_id:
                    user_ids = self._fields['user_ids'].convert_to_cache(vals.get('user_ids', []), self)
                    if self.env.user.id not in user_ids and not is_superuser:
                        vals['user_ids'] = [Command.set(list(user_ids) + [self.env.uid])]
            # Stage change: Update date_end if folded stage and date_last_stage_update
            if vals.get('stage_id'):
                vals.update(self.update_date_end(vals['stage_id']))
                vals['date_last_stage_update'] = fields.Datetime.now()
            # recurrence
            rec_fields = vals.keys() & self._get_recurrence_fields()
            if rec_fields and vals.get('recurring_task') is True:
                rec_values = {rec_field: vals[rec_field] for rec_field in rec_fields}
                rec_values['next_recurrence_date'] = fields.Datetime.today()
                recurrence = self.env['project.task.recurrence'].create(rec_values)
                vals['recurrence_id'] = recurrence.id
        # The sudo is required for a portal user as the record creation
        # requires the read access on other models, as mail.template
        # in order to compute the field tracking
        was_in_sudo = self.env.su
        if is_portal_user:
            vals_list_no_sudo, vals_list = zip(*(self._get_portal_sudo_vals(vals, defaults=True) for vals in vals_list))
            self_no_sudo, self = self, self.with_context(self._get_portal_sudo_context()).sudo()
        tasks = super(Task, self).create(vals_list)
        if is_portal_user:
            for task, vals in zip(tasks.with_env(self_no_sudo.env), vals_list_no_sudo):
                task.write(vals)
        tasks._populate_missing_personal_stages()
        self._task_message_auto_subscribe_notify({task: task.user_ids - self.env.user for task in tasks})

        # in case we were already in sudo, we don't check the rights.
        if is_portal_user and not was_in_sudo:
            # since we use sudo to create tasks, we need to check
            # if the portal user could really create the tasks based on the ir rule.
            tasks.with_user(self.env.user).check_access_rule('create')
        current_partner = self.env.user.partner_id
        for task in tasks:
            if task.project_id.privacy_visibility == 'portal':
                task._portal_ensure_token()
            if current_partner not in task.message_partner_ids:
                task.message_subscribe(current_partner.ids)
        return tasks

    def write(self, vals):
        if len(self) == 1:
            handle_history_divergence(self, 'description', vals)
        portal_can_write = False
        if self.env.user.has_group('base.group_portal') and not self.env.su:
            # Check if all fields in vals are in SELF_WRITABLE_FIELDS
            self._ensure_fields_are_accessible(vals.keys(), operation='write', check_group_user=False)
            self.check_access_rights('write')
            self.check_access_rule('write')
            portal_can_write = True

        now = fields.Datetime.now()
        if 'parent_id' in vals and vals['parent_id'] in self.ids:
            raise UserError(_("Sorry. You can't set a task as its parent task."))
        if 'active' in vals and not vals.get('active') and any(self.mapped('recurrence_id')):
            vals['recurring_task'] = False
        if 'recurrence_id' in vals and vals.get('recurrence_id') and any(not task.active for task in self):
            raise UserError(_('Archived tasks cannot be recurring. Please unarchive the task first.'))
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            if not 'project_id' in vals and self.filtered(lambda t: not t.project_id):
                raise UserError(_('You can only set a personal stage on a private task.'))

            vals.update(self.update_date_end(vals['stage_id']))
            vals['date_last_stage_update'] = now
        task_ids_without_user_set = set()
        if 'user_ids' in vals and 'date_assign' not in vals:
            # prepare update of date_assign after super call
            task_ids_without_user_set = {task.id for task in self if not task.user_ids}

        # recurrence fields
        rec_fields = vals.keys() & self._get_recurrence_fields()
        if rec_fields:
            rec_values = {rec_field: vals[rec_field] for rec_field in rec_fields}
            for task in self:
                if task.recurrence_id:
                    task.recurrence_id.write(rec_values)
                elif vals.get('recurring_task'):
                    rec_values['next_recurrence_date'] = fields.Datetime.today()
                    recurrence = self.env['project.task.recurrence'].create(rec_values)
                    task.recurrence_id = recurrence.id

        if not vals.get('recurring_task', True) and self.recurrence_id:
            tasks_in_recurrence = self.recurrence_id.task_ids
            self.recurrence_id.unlink()
            tasks_in_recurrence.write({'recurring_task': False})

        tasks = self
        recurrence_update = vals.pop('recurrence_update', 'this')
        if recurrence_update != 'this':
            recurrence_domain = []
            if recurrence_update == 'subsequent':
                for task in self:
                    recurrence_domain = expression.OR([recurrence_domain, ['&', ('recurrence_id', '=', task.recurrence_id.id), ('create_date', '>=', task.create_date)]])
            else:
                recurrence_domain = [('recurrence_id', 'in', self.recurrence_id.ids)]
            tasks |= self.env['project.task'].search(recurrence_domain)

        # The sudo is required for a portal user as the record update
        # requires the write access on others models, as rating.rating
        # in order to keep the same name than the task.
        if portal_can_write:
            tasks_no_sudo, tasks = tasks, tasks.sudo()
            vals_no_sudo, vals = self._get_portal_sudo_vals(vals)

        # Track user_ids to send assignment notifications
        old_user_ids = {t: t.user_ids for t in self}

        if "personal_stage_type_id" in vals and not vals['personal_stage_type_id']:
            del vals['personal_stage_type_id']

        result = super(Task, tasks).write(vals)
        if portal_can_write:
            super(Task, tasks_no_sudo).write(vals_no_sudo)

        if 'user_ids' in vals:
            tasks._populate_missing_personal_stages()

        # user_ids change: update date_assign
        if 'user_ids' in vals:
            for task in self:
                if not task.user_ids and task.date_assign:
                    task.date_assign = False
                elif 'date_assign' not in vals and task.id in task_ids_without_user_set:
                    task.date_assign = now

        # rating on stage
        if 'stage_id' in vals and vals.get('stage_id'):
            tasks.filtered(lambda x: x.project_id.rating_active and x.project_id.rating_status == 'stage')._send_task_rating_mail(force_send=True)
        for task in tasks:
            if task.display_project_id != task.project_id and not task.parent_id:
                # We must make the display_project_id follow the project_id if no parent_id set
                task.display_project_id = task.project_id

        self._task_message_auto_subscribe_notify({task: task.user_ids - old_user_ids[task] - self.env.user for task in self})
        return result

    def update_date_end(self, stage_id):
        project_task_type = self.env['project.task.type'].browse(stage_id)
        if project_task_type.fold:
            return {'date_end': fields.Datetime.now()}
        return {'date_end': False}

    @api.ondelete(at_uninstall=False)
    def _unlink_except_recurring(self):
        if any(self.mapped('recurrence_id')):
            # TODO: show a dialog to stop the recurrence
            raise UserError(_('You cannot delete recurring tasks. Please disable the recurrence first.'))

    # ---------------------------------------------------
    # Subtasks
    # ---------------------------------------------------

    @api.depends('parent_id', 'project_id', 'display_project_id')
    def _compute_partner_id(self):
        """ Compute the partner_id when the tasks have no partner_id.

            Use the project partner_id if any, or else the parent task partner_id.
        """
        for task in self.filtered(lambda task: not task.partner_id):
            # When the task has a parent task, the display_project_id can be False or the project choose by the user for this task.
            project = task.display_project_id if task.parent_id and task.display_project_id else task.project_id
            task.partner_id = self._get_default_partner_id(project, task.parent_id)

    @api.depends('partner_id.email', 'parent_id.email_from')
    def _compute_email_from(self):
        for task in self:
            task.email_from = task.partner_id.email or ((task.partner_id or task.parent_id) and task.email_from) or task.parent_id.email_from

    @api.depends('parent_id.project_id', 'display_project_id')
    def _compute_project_id(self):
        # Avoid recomputing kanban_state
        self.env.remove_to_compute(self._fields['kanban_state'], self)
        for task in self:
            if task.parent_id:
                task.project_id = task.display_project_id or task.parent_id.project_id

    @api.depends('project_id')
    def _compute_milestone_id(self):
        for task in self:
            if task.project_id != task.milestone_id.project_id:
                task.milestone_id = False

    def _compute_has_late_and_unreached_milestone(self):
        if all(not task.allow_milestones for task in self):
            self.has_late_and_unreached_milestone = False
            return
        late_milestones = self.env['project.milestone'].sudo()._search([  # sudo is needed for the portal user in Project Sharing.
            ('id', 'in', self.milestone_id.ids),
            ('is_reached', '=', False),
            ('deadline', '<', fields.Date.today()),
        ])
        for task in self:
            task.has_late_and_unreached_milestone = task.allow_milestones and task.milestone_id.id in late_milestones

    def _search_has_late_and_unreached_milestone(self, operator, value):
        if operator not in ('=', '!=') or not isinstance(value, bool):
            raise NotImplementedError(_('The search does not support the %s operator or %s value.', operator, value))
        domain = [
            ('allow_milestones', '=', True),
            ('milestone_id', '!=', False),
            ('milestone_id.is_reached', '=', False),
            ('milestone_id.deadline', '!=', False), ('milestone_id.deadline', '<', fields.Date.today())
        ]
        if (operator == '!=' and value) or (operator == '=' and not value):
            domain.insert(0, expression.NOT_OPERATOR)
            domain = expression.distribute_not(domain)
        return domain

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _notify_by_email_prepare_rendering_context(self, message, msg_vals=False, model_description=False,
                                                   force_email_company=False, force_email_lang=False):
        render_context = super()._notify_by_email_prepare_rendering_context(
            message, msg_vals, model_description=model_description,
            force_email_company=force_email_company, force_email_lang=force_email_lang
        )
        if self.date_deadline:
            render_context['subtitles'].append(
                _('Deadline: %s', self.date_deadline.strftime(get_lang(self.env).date_format)))
        elif self.date_assign:
            render_context['subtitles'].append(
                _('Assigned On: %s', self.date_assign.strftime(get_lang(self.env).date_format)))
        return render_context

    @api.model
    def _task_message_auto_subscribe_notify(self, users_per_task):
        # Utility method to send assignation notification upon writing/creation.
        template_id = self.env['ir.model.data']._xmlid_to_res_id('project.project_message_user_assigned', raise_if_not_found=False)
        if not template_id:
            return
        task_model_description = self.env['ir.model']._get(self._name).display_name
        for task, users in users_per_task.items():
            if not users:
                continue
            values = {
                'object': task,
                'model_description': task_model_description,
                'access_link': task._notify_get_action_link('view'),
            }
            for user in users:
                values.update(assignee_name=user.sudo().name)
                assignation_msg = self.env['ir.qweb']._render('project.project_message_user_assigned', values, minimal_qcontext=True)
                assignation_msg = self.env['mail.render.mixin']._replace_local_links(assignation_msg)
                task.message_notify(
                    subject=_('You have been assigned to %s', task.display_name),
                    body=assignation_msg,
                    partner_ids=user.partner_id.ids,
                    record_name=task.display_name,
                    email_layout_xmlid='mail.mail_notification_layout',
                    model_description=task_model_description,
                    mail_auto_delete=False,
                )

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        if 'user_ids' not in updated_values:
            return []
        # Since the changes to user_ids becoming a m2m, the default implementation of this function
        #  could not work anymore, override the function to keep the functionality.
        new_followers = []
        # Normalize input to tuple of ids
        value = self._fields['user_ids'].convert_to_cache(updated_values.get('user_ids', []), self.env['project.task'], validate=False)
        users = self.env['res.users'].browse(value)
        for user in users:
            try:
                if user.partner_id:
                    # The you have been assigned notification is handled separately
                    new_followers.append((user.partner_id.id, default_subtype_ids, False))
            except Exception:
                pass
        return new_followers

    def _mail_track(self, tracked_fields, initial_values):
        changes, tracking_value_ids = super()._mail_track(tracked_fields, initial_values)
        # Many2many tracking
        if len(changes) > len(tracking_value_ids):
            for changed_field in changes:
                if tracked_fields[changed_field]['type'] in ['one2many', 'many2many']:
                    field = self.env['ir.model.fields']._get(self._name, changed_field)
                    vals = {
                        'field': field.id,
                        'field_desc': field.field_description,
                        'field_type': field.ttype,
                        'tracking_sequence': field.tracking,
                        'old_value_char': ', '.join(initial_values[changed_field].mapped('name')),
                        'new_value_char': ', '.join(self[changed_field].mapped('name')),
                    }
                    tracking_value_ids.append(Command.create(vals))
        # Track changes on depending tasks
        depends_tracked_fields = self._get_depends_tracked_fields()
        depends_changes = changes & depends_tracked_fields
        if depends_changes and self.allow_task_dependencies and self.user_has_groups('project.group_project_task_dependencies'):
            parent_ids = self.dependent_ids
            if parent_ids:
                fields_to_ids = self.env['ir.model.fields']._get_ids('project.task')
                field_ids = [fields_to_ids.get(name) for name in depends_changes]
                depends_tracking_value_ids = [
                    tracking_values for tracking_values in tracking_value_ids
                    if tracking_values[2]['field'] in field_ids
                ]
                subtype = self.env['ir.model.data']._xmlid_to_res_id('project.mt_task_dependency_change')
                # We want to include the original subtype message coming from the child task
                # for example when the stage changes the message in the chatter starts with 'Stage Changed'
                child_subtype = self._track_subtype(dict((col_name, initial_values[col_name]) for col_name in changes))
                child_subtype_info = child_subtype.description or child_subtype.name if child_subtype else False
                # NOTE: the subtype does not have a description on purpose, otherwise the description would be put
                #  at the end of the message instead of at the top, we use the name here
                body = self.env['ir.qweb']._render('project.task_track_depending_tasks', {
                    'child': self,
                    'child_subtype': child_subtype_info,
                })
                for p in parent_ids:
                    p.message_post(body=body, subtype_id=subtype, tracking_value_ids=depends_tracking_value_ids)
        return changes, tracking_value_ids

    def _track_template(self, changes):
        res = super(Task, self)._track_template(changes)
        test_task = self[0]
        if 'stage_id' in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })
        return res

    def _creation_subtype(self):
        return self.env.ref('project.mt_task_new')

    def _track_subtype(self, init_values):
        self.ensure_one()
        mail_message_subtype_per_kanban_state = {
            'blocked': 'project.mt_task_blocked',
            'done': 'project.mt_task_ready',
            'normal': 'project.mt_task_progress',
        }
        if 'stage_id' in init_values:
            return self.env.ref('project.mt_task_stage')
        elif 'kanban_state_label' in init_values and self.kanban_state in mail_message_subtype_per_kanban_state:
            return self.env.ref(mail_message_subtype_per_kanban_state[self.kanban_state])
        return super(Task, self)._track_subtype(init_values)

    def _mail_get_message_subtypes(self):
        res = super()._mail_get_message_subtypes()
        if len(self) == 1:
            dependency_subtype = self.env.ref('project.mt_task_dependency_change')
            if ((self.project_id and not self.project_id.allow_task_dependencies)\
                or (not self.project_id and not self.user_has_groups('project.group_project_task_dependencies')))\
                and dependency_subtype in res:
                res -= dependency_subtype
        return res

    def _notify_get_recipients_groups(self, msg_vals=None):
        """ Handle project users and managers recipients that can assign
        tasks and create new one directly from notification emails. Also give
        access button to portal users and portal customers. If they are notified
        they should probably have access to the document. """
        groups = super(Task, self)._notify_get_recipients_groups(msg_vals=msg_vals)
        if not self:
            return groups

        local_msg_vals = dict(msg_vals or {})
        self.ensure_one()

        project_user_group_id = self.env.ref('project.group_project_user').id
        new_group = ('group_project_user', lambda pdata: pdata['type'] == 'user' and project_user_group_id in pdata['groups'], {})
        groups = [new_group] + groups

        if self.project_privacy_visibility == 'portal':
            groups.insert(0, (
                'allowed_portal_users',
                lambda pdata: pdata['type'] == 'portal',
                {}
            ))
        portal_privacy = self.project_id.privacy_visibility == 'portal'
        for group_name, _group_method, group_data in groups:
            if group_name in ('customer', 'user') or group_name == 'portal_customer' and not portal_privacy:
                group_data['has_button_access'] = False
            elif group_name == 'portal_customer' and portal_privacy:
                group_data['has_button_access'] = True

        return groups

    def _notify_get_reply_to(self, default=None):
        """ Override to set alias of tasks to their project if any. """
        aliases = self.sudo().mapped('project_id')._notify_get_reply_to(default=default)
        res = {task.id: aliases.get(task.project_id.id) for task in self}
        leftover = self.filtered(lambda rec: not rec.project_id)
        if leftover:
            res.update(super(Task, leftover)._notify_get_reply_to(default=default))
        return res

    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        aliases = self.mapped('project_id.alias_name')
        return [x for x in email_list if x.split('@')[0] not in aliases]

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        create_context = dict(self.env.context or {})
        create_context['default_user_ids'] = False
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'planned_hours': 0.0,
            'partner_id': msg.get('author_id'),
        }
        defaults.update(custom_values)

        task = super(Task, self.with_context(create_context)).message_new(msg, custom_values=defaults)
        email_list = task.email_split(msg)
        partner_ids = [p.id for p in self.env['mail.thread']._mail_find_partner_from_emails(email_list, records=task, force_create=False) if p]
        task.message_subscribe(partner_ids)
        return task

    def message_update(self, msg, update_vals=None):
        """ Override to update the task according to the email. """
        email_list = self.email_split(msg)
        partner_ids = [p.id for p in self.env['mail.thread']._mail_find_partner_from_emails(email_list, records=self, force_create=False) if p]
        self.message_subscribe(partner_ids)
        return super(Task, self).message_update(msg, update_vals=update_vals)

    def _message_get_suggested_recipients(self):
        recipients = super(Task, self)._message_get_suggested_recipients()
        for task in self:
            if task.partner_id:
                reason = _('Customer Email') if task.partner_id.email else _('Customer')
                task._message_add_suggested_recipient(recipients, partner=task.partner_id, reason=reason)
            elif task.email_from:
                task._message_add_suggested_recipient(recipients, email=task.email_from, reason=_('Customer Email'))
        return recipients

    def _notify_by_email_get_headers(self):
        headers = super(Task, self)._notify_by_email_get_headers()
        if self.project_id:
            current_objects = [h for h in headers.get('X-Odoo-Objects', '').split(',') if h]
            current_objects.insert(0, 'project.project-%s, ' % self.project_id.id)
            headers['X-Odoo-Objects'] = ','.join(current_objects)
        if self.tag_ids:
            headers['X-Odoo-Tags'] = ','.join(self.tag_ids.mapped('name'))
        return headers

    def _message_post_after_hook(self, message, msg_vals):
        if message.attachment_ids and not self.displayed_image_id:
            image_attachments = message.attachment_ids.filtered(lambda a: a.mimetype == 'image')
            if image_attachments:
                self.displayed_image_id = image_attachments[0]

        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            email_normalized = tools.email_normalize(self.email_from)
            new_partner = message.partner_ids.filtered(
                lambda partner: partner.email == self.email_from or (email_normalized and partner.email_normalized == email_normalized)
            )
            if new_partner:
                if new_partner[0].email_normalized:
                    email_domain = ('email_from', 'in', [new_partner[0].email, new_partner[0].email_normalized])
                else:
                    email_domain = ('email_from', '=', new_partner[0].email)
                self.search([
                    ('partner_id', '=', False), email_domain, ('stage_id.fold', '=', False)
                ]).write({'partner_id': new_partner[0].id})
        # use the sanitized body of the email from the message thread to populate the task's description
        if not self.description and message.subtype_id == self._creation_subtype() and self.partner_id == message.author_id:
            self.description = message.body
        return super(Task, self)._message_post_after_hook(message, msg_vals)

    def action_assign_to_me(self):
        self.write({'user_ids': [(4, self.env.user.id)]})

    def action_unassign_me(self):
        self.write({'user_ids': [Command.unlink(self.env.uid)]})

    def _get_all_subtasks(self, depth=0):
        return self.browse(set.union(set(), *self._get_subtask_ids_per_task_id().values()))

    def _get_subtask_ids_per_task_id(self):
        if not self:
            return {}

        res = dict.fromkeys(self._ids, [])
        if all(self._ids):
            self.env.cr.execute(
                """
         WITH RECURSIVE task_tree
                     AS (
                     SELECT id, id as supertask_id
                       FROM project_task
                      WHERE id IN %(ancestor_ids)s
                      UNION
                         SELECT t.id, tree.supertask_id
                           FROM project_task t
                           JOIN task_tree tree
                             ON tree.id = t.parent_id
                            AND t.active in (TRUE, %(active)s)
               ) SELECT supertask_id, ARRAY_AGG(id)
                   FROM task_tree
                  WHERE id != supertask_id
               GROUP BY supertask_id
                """,
                {
                    "ancestor_ids": tuple(self.ids),
                    "active": self._context.get('active_test', True),
                }
            )
            res.update(dict(self.env.cr.fetchall()))
        else:
            res.update({
                task.id: task._get_subtasks_recursively().ids
                for task in self
            })
        return res

    def _get_subtasks_recursively(self):
        children = self.child_ids
        if not children:
            return self.env['project.task']
        return children + children._get_subtasks_recursively()

    def action_open_parent_task(self):
        return {
            'name': _('Parent Task'),
            'view_mode': 'form',
            'res_model': 'project.task',
            'res_id': self.parent_id.id,
            'type': 'ir.actions.act_window',
            'context': self._context
        }

    def action_project_sharing_view_parent_task(self):
        if self.parent_id.project_id != self.project_id and self.user_has_groups('base.group_portal'):
            project = self.parent_id.project_id._filter_access_rules_python('read')
            if project:
                url = f"/my/projects/{self.parent_id.project_id.id}/task/{self.parent_id.id}"
                if project._check_project_sharing_access():
                    url = f"/my/projects/{self.parent_id.project_id.id}?task_id={self.parent_id.id}"
                return {
                    "name": "Portal Parent Task",
                    "type": "ir.actions.act_url",
                    "url": url,
                }
            elif self.display_parent_task_button:
                return self.parent_id.get_portal_url()
            # The portal user has no access to the parent task, so normally the button should be invisible.
            return {}
        action = self.action_open_parent_task()
        action['views'] = [(self.env.ref('project.project_sharing_project_task_view_form').id, 'form')]
        return action

    # ------------
    # Actions
    # ------------

    def action_open_task(self):
        return {
            'view_mode': 'form',
            'res_model': 'project.task',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'context': self._context
        }

    def action_project_sharing_open_task(self):
        action = self.action_open_task()
        action['views'] = [[self.env.ref('project.project_sharing_project_task_view_form').id, 'form']]
        return action

    def action_project_sharing_open_subtasks(self):
        self.ensure_one()
        subtasks = self.env['project.task'].search([('id', 'child_of', self.id), ('id', '!=', self.id)])
        if subtasks.project_id == self.project_id:
            action = self.env['ir.actions.act_window']._for_xml_id('project.project_sharing_project_task_action_sub_task')
            if len(subtasks) == 1:
                action['view_mode'] = 'form'
                action['views'] = [(view_id, view_type) for view_id, view_type in action['views'] if view_type == 'form']
                action['res_id'] = subtasks.id
            return action
        return {
            'name': 'Portal Sub-tasks',
            'type': 'ir.actions.act_url',
            'url': f'/my/projects/{self.project_id.id}/task/{self.id}/subtasks' if len(subtasks) > 1 else subtasks.get_portal_url(query_string='project_sharing=1'),
        }

    def action_dependent_tasks(self):
        self.ensure_one()
        action = {
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'context': {**self._context, 'default_depend_on_ids': [Command.link(self.id)], 'show_project_update': False},
        }
        if self.dependent_tasks_count == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.dependent_ids.id
            action['views'] = [(False, 'form')]
        else:
            action['domain'] = [('depend_on_ids', '=', self.id)]
            action['name'] = _('Dependent Tasks')
            action['view_mode'] = 'tree,form,kanban,calendar,pivot,graph,activity'
        return action

    def action_recurring_tasks(self):
        return {
            'name': _('Tasks in Recurrence'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'tree,form,kanban,calendar,pivot,graph,activity',
            'context': {'create': False},
            'domain': [('recurrence_id', 'in', self.recurrence_id.ids)],
        }

    def action_open_ratings(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('project.rating_rating_action_task')
        if self.rating_count == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.rating_ids[0].id
            action['views'] = [[self.env.ref('project.rating_rating_view_form_project').id, 'form']]
            return action
        else:
            return action

    def action_stop_recurrence(self):
        tasks = self.env['project.task'].with_context(active_test=False).search([('recurrence_id', 'in', self.recurrence_id.ids)])
        tasks.write({'recurring_task': False})
        self.recurrence_id.unlink()

    def action_continue_recurrence(self):
        self.recurrence_id = False
        self.recurring_task = False

    # ---------------------------------------------------
    # Rating business
    # ---------------------------------------------------

    def _send_task_rating_mail(self, force_send=False):
        for task in self:
            rating_template = task.stage_id.rating_template_id
            if rating_template:
                task.rating_send_request(rating_template, lang=task.partner_id.lang, force_send=force_send)

    def _rating_get_partner(self):
        res = super(Task, self)._rating_get_partner()
        if not res and self.project_id.partner_id:
            return self.project_id.partner_id
        return res

    def rating_apply(self, rate, token=None, rating=None, feedback=None,
                     subtype_xmlid=None, notify_delay_send=False):
        rating = super(Task, self).rating_apply(
            rate, token=token, rating=rating, feedback=feedback,
            subtype_xmlid=subtype_xmlid, notify_delay_send=notify_delay_send)
        if self.stage_id and self.stage_id.auto_validation_kanban_state:
            kanban_state = 'done' if rating.rating >= rating_data.RATING_LIMIT_OK else 'blocked'
            self.write({'kanban_state': kanban_state})
        return rating

    def _rating_apply_get_default_subtype_id(self):
        return self.env['ir.model.data']._xmlid_to_res_id("project.mt_task_rating")

    def _rating_get_parent_field_name(self):
        return 'project_id'

    def _rating_get_operator(self):
        """ Overwrite since we have user_ids and not user_id """
        tasks_with_one_user = self.filtered(lambda task: len(task.user_ids) == 1 and task.user_ids.partner_id)
        return tasks_with_one_user.user_ids.partner_id or self.env['res.partner']

    # ---------------------------------------------------
    # Privacy
    # ---------------------------------------------------
    def _unsubscribe_portal_users(self):
        self.message_unsubscribe(partner_ids=self.message_partner_ids.filtered('user_ids.share').ids)

    # ---------------------------------------------------
    # Analytic accounting
    # ---------------------------------------------------
    def _get_task_analytic_account_id(self):
        self.ensure_one()
        return self.analytic_account_id or self.project_analytic_account_id

    @api.model
    def get_unusual_days(self, date_from, date_to=None):
        calendar = self.env.company.resource_calendar_id
        return calendar._get_unusual_days(
            datetime.combine(fields.Date.from_string(date_from), time.min).replace(tzinfo=UTC),
            datetime.combine(fields.Date.from_string(date_to), time.max).replace(tzinfo=UTC)
        )