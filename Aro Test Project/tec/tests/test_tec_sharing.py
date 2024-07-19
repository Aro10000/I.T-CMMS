# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import Command
from odoo.osv import expression
from odoo.exceptions import AccessError
from odoo.tools import mute_logger
from odoo.tests import tagged
from odoo.tests.common import Form

from .test_tec_base import TestTecCommon


class TestTecSharingCommon(TestTecCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        tec_sharing_stages_vals_list = [
            (0, 0, {'name': 'To Do', 'sequence': 1}),
            (0, 0, {'name': 'Done', 'sequence': 10, 'fold': True, 'rating_template_id': cls.env.ref('tec.rating_tec_request_email_template').id}),
        ]

        cls.partner_portal = cls.env['res.partner'].create({
            'name': 'Chell Gladys',
            'email': 'chell@gladys.portal',
            'company_id': False,
            'user_ids': [Command.link(cls.user_portal.id)]})

        cls.tec_cows = cls.env['tec.tec'].with_context({'mail_create_nolog': True}).create({
            'name': 'Cows',
            'privacy_visibility': 'portal',
            'alias_name': 'tec+cows',
            'type_ids': tec_sharing_stages_vals_list,
        })
        cls.tec_portal = cls.env['tec.tec'].with_context({'mail_create_nolog': True}).create({
            'name': 'Portal',
            'privacy_visibility': 'portal',
            'alias_name': 'tec+portal',
            'partner_id': cls.user_portal.partner_id.id,
            'type_ids': tec_sharing_stages_vals_list,
        })
        cls.tec_portal.message_subscribe(partner_ids=[cls.partner_portal.id])

        cls.tec_no_collabo = cls.env['tec.tec'].with_context({'mail_create_nolog': True}).create({
            'name': 'No Collabo',
            'privacy_visibility': 'followers',
            'alias_name': 'tec+nocollabo',
        })

        cls.task_cow = cls.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Cow UserTask',
            'user_ids': cls.user_tecuser,
            'tec_id': cls.tec_cows.id,
        })
        cls.task_portal = cls.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Portal UserTask',
            'user_ids': cls.user_tecuser,
            'tec_id': cls.tec_portal.id,
        })
        cls.task_no_collabo = cls.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'No Collabo Task',
            'tec_id': cls.tec_no_collabo.id,
        })

        cls.task_tag = cls.env['tec.tags'].create({'name': 'Foo'})

        cls.tec_sharing_form_view_xml_id = 'tec.tec_sharing_tec_task_view_form'

    def get_tec_sharing_form_view(self, record, with_user=None):
        return Form(
            record.with_user(with_user or self.env.user),
            view=self.tec_sharing_form_view_xml_id
        )

@tagged('tec_sharing')
class TestTecSharing(TestTecSharingCommon):

    def test_tec_share_wizard(self):
        """ Test Tec Share Wizard

            Test Cases:
            ==========
            1) Create the wizard record
            2) Check if no access rights are given to a portal user
            3) Add access rights to a portal user
        """
        tec_share_wizard = self.env['tec.share.wizard'].create({
            'res_model': 'tec.tec',
            'res_id': self.tec_portal.id,
            'access_mode': 'edit',
        })
        self.assertFalse(tec_share_wizard.partner_ids, 'No collaborator should be in the wizard.')
        self.assertFalse(self.tec_portal.with_user(self.user_portal)._check_tec_sharing_access(), 'The portal user should not have accessed in tec sharing views.')
        tec_share_wizard.write({'partner_ids': [Command.link(self.user_portal.partner_id.id)]})
        tec_share_wizard.action_send_mail()
        self.assertEqual(len(self.tec_portal.collaborator_ids), 1, 'The access right added in tec share wizard should be added in the tec when the user confirm the access in the wizard.')
        self.assertDictEqual({
            'partner_id': self.tec_portal.collaborator_ids.partner_id,
            'tec_id': self.tec_portal.collaborator_ids.tec_id,
        }, {
            'partner_id': self.user_portal.partner_id,
            'tec_id': self.tec_portal,
        }, 'The access rights added should be the read access for the portal tec for Chell Gladys.')
        self.assertTrue(self.tec_portal.with_user(self.user_portal)._check_tec_sharing_access(), 'The portal user should have read access to the portal tec with tec sharing feature.')

    def test_tec_sharing_access(self):
        """ Check if the different user types can access to tec sharing feature as expected. """
        with self.assertRaises(AccessError, msg='The public user should not have any access to tec sharing feature of the portal tec.'):
            self.tec_portal.with_user(self.user_public)._check_tec_sharing_access()
        self.assertTrue(self.tec_portal.with_user(self.user_tecuser)._check_tec_sharing_access(), 'The internal user should have all accesses to tec sharing feature of the portal tec.')
        self.assertFalse(self.tec_portal.with_user(self.user_portal)._check_tec_sharing_access(), 'The portal user should not have any access to tec sharing feature of the portal tec.')
        self.tec_portal.write({'collaborator_ids': [Command.create({'partner_id': self.user_portal.partner_id.id})]})
        self.assertTrue(self.tec_portal.with_user(self.user_portal)._check_tec_sharing_access(), 'The portal user can access to tec sharing feature of the portal tec.')

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_create_task_in_tec_sharing(self):
        """ Test when portal user creates a task in tec sharing views.

            Test Cases:
            ==========
            1) Give the 'read' access mode to a portal user in a tec and try to create task with this user.
            2) Give the 'comment' access mode to a portal user in a tec and try to create task with this user.
            3) Give the 'edit' access mode to a portal user in a tec and try to create task with this user.
            3.1) Try to change the tec of the new task with this user.
        """
        self.tec_portal.allow_subtasks = True
        Task = self.env['tec.task'].with_context({'tracking_disable': True, 'default_tec_id': self.tec_portal.id, 'default_user_ids': [(4, self.user_portal.id)]})
        # 1) Give the 'read' access mode to a portal user in a tec and try to create task with this user.
        with self.assertRaises(AccessError, msg="Should not accept the portal user create a task in the tec when he has not the edit access right."):
            with self.get_tec_sharing_form_view(Task, self.user_portal) as form:
                form.name = 'Test'
                task = form.save()

        self.tec_portal.write({
            'collaborator_ids': [
                Command.create({'partner_id': self.user_portal.partner_id.id}),
            ],
        })
        with self.get_tec_sharing_form_view(Task, self.user_portal) as form:
            form.name = 'Test'
            with form.child_ids.new() as subtask_form:
                subtask_form.name = 'Test Subtask'
            task = form.save()
            self.assertEqual(task.name, 'Test')
            self.assertEqual(task.tec_id, self.tec_portal)
            self.assertFalse(task.portal_user_names)

            # Check creating a sub-task while creating the parent task works as expected.
            self.assertEqual(task.child_ids.name, 'Test Subtask')
            self.assertEqual(task.child_ids.tec_id, self.tec_portal)
            self.assertFalse(task.child_ids.portal_user_names, 'by default no user should be assigned to a subtask created by the portal user.')
            self.assertFalse(task.child_ids.user_ids, 'No user should be assigned to the new subtask.')

            # 3.1) Try to change the tec of the new task with this user.
            with self.assertRaises(AssertionError, msg="Should not accept the portal user changes the tec of the task."):
                form.tec_id = self.tec_cows
                task = form.save()

        Task = Task.with_user(self.user_portal)
        # Create/Update a forbidden task through child_ids
        with self.assertRaisesRegex(AccessError, "You cannot write on description"):
            Task.create({'name': 'foo', 'child_ids': [Command.create({'name': 'Foo', 'description': 'Foo'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.create({'name': 'foo', 'child_ids': [Command.update(self.task_no_collabo.id, {'name': 'Foo'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to delete 'Task'"):
            Task.create({'name': 'foo', 'child_ids': [Command.delete(self.task_no_collabo.id)]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.create({'name': 'foo', 'child_ids': [Command.unlink(self.task_no_collabo.id)]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.create({'name': 'foo', 'child_ids': [Command.link(self.task_no_collabo.id)]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.create({'name': 'foo', 'child_ids': [Command.set([self.task_no_collabo.id])]})

        # Same thing but using context defaults
        with self.assertRaisesRegex(AccessError, "You cannot write on description"):
            Task.with_context(default_child_ids=[Command.create({'name': 'Foo', 'description': 'Foo'})]).create({'name': 'foo'})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.with_context(default_child_ids=[Command.update(self.task_no_collabo.id, {'name': 'Foo'})]).create({'name': 'foo'})
        with self.assertRaisesRegex(AccessError, "not allowed to delete 'Task'"):
            Task.with_context(default_child_ids=[Command.delete(self.task_no_collabo.id)]).create({'name': 'foo'})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.with_context(default_child_ids=[Command.unlink(self.task_no_collabo.id)]).create({'name': 'foo'})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.with_context(default_child_ids=[Command.link(self.task_no_collabo.id)]).create({'name': 'foo'})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            Task.with_context(default_child_ids=[Command.set([self.task_no_collabo.id])]).create({'name': 'foo'})

        # Create/update a tag through tag_ids
        with self.assertRaisesRegex(AccessError, "not allowed to create 'Tec Tags'"):
            Task.create({'name': 'foo', 'tag_ids': [Command.create({'name': 'Bar'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Tec Tags'"):
            Task.create({'name': 'foo', 'tag_ids': [Command.update(self.task_tag.id, {'name': 'Bar'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to delete 'Tec Tags'"):
            Task.create({'name': 'foo', 'tag_ids': [Command.delete(self.task_tag.id)]})

        # Same thing but using context defaults
        with self.assertRaisesRegex(AccessError, "not allowed to create 'Tec Tags'"):
            Task.with_context(default_tag_ids=[Command.create({'name': 'Bar'})]).create({'name': 'foo'})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Tec Tags'"):
            Task.with_context(default_tag_ids=[Command.update(self.task_tag.id, {'name': 'Bar'})]).create({'name': 'foo'})
        with self.assertRaisesRegex(AccessError, "not allowed to delete 'Tec Tags'"):
            Task.with_context(default_tag_ids=[Command.delete(self.task_tag.id)]).create({'name': 'foo'})

        task = Task.create({'name': 'foo', 'tag_ids': [Command.link(self.task_tag.id)]})
        self.assertEqual(task.tag_ids, self.task_tag)

        Task.create({'name': 'foo', 'tag_ids': [Command.set([self.task_tag.id])]})
        self.assertEqual(task.tag_ids, self.task_tag)

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_edit_task_in_tec_sharing(self):
        """ Test when portal user creates a task in tec sharing views.

            Test Cases:
            ==========
            1) Give the 'read' access mode to a portal user in a tec and try to edit task with this user.
            2) Give the 'comment' access mode to a portal user in a tec and try to edit task with this user.
            3) Give the 'edit' access mode to a portal user in a tec and try to create task with this user.
            3.1) Try to change the tec of the new task with this user.
            3.2) Create a sub-task
            3.3) Create a second sub-task
        """
        # 0) Allow to create subtasks in the tec tasks
        # Required for `child_ids` to be visible in the view
        # {'invisible': [('allow_subtasks', '=', False)]}
        self.tec_cows.allow_subtasks = True
        # 1) Give the 'read' access mode to a portal user in a tec and try to create task with this user.
        with self.assertRaises(AccessError, msg="Should not accept the portal user create a task in the tec when he has not the edit access right."):
            with self.get_tec_sharing_form_view(self.task_cow.with_context({'tracking_disable': True, 'default_tec_id': self.tec_cows.id}), self.user_portal) as form:
                form.name = 'Test'
                task = form.save()

        tec_share_wizard = self.env['tec.share.wizard'].create({
            'access_mode': 'edit',
            'res_model': 'tec.tec',
            'res_id': self.tec_cows.id,
            'partner_ids': [
                Command.link(self.user_portal.partner_id.id),
            ],
        })
        tec_share_wizard.action_send_mail()

        with self.get_tec_sharing_form_view(self.task_cow.with_context({'tracking_disable': True, 'default_tec_id': self.tec_cows.id, 'uid': self.user_portal.id}), self.user_portal) as form:
            form.name = 'Test'
            task = form.save()
            self.assertEqual(task.name, 'Test')
            self.assertEqual(task.tec_id, self.tec_cows)

        # 3.1) Try to change the tec of the new task with this user.
        with self.assertRaises(AssertionError, msg="Should not accept the portal user changes the tec of the task."):
            with self.get_tec_sharing_form_view(task, self.user_portal) as form:
                form.tec_id = self.tec_portal

        # 3.2) Create a sub-task
        with self.get_tec_sharing_form_view(task, self.user_portal) as form:
            with form.child_ids.new() as subtask_form:
                subtask_form.name = 'Test Subtask'
                with self.assertRaises(AssertionError, msg="Should not accept the portal user changes the tec of the task."):
                    subtask_form.display_tec_id = self.tec_portal
        self.assertEqual(task.child_ids.name, 'Test Subtask')
        self.assertEqual(task.child_ids.tec_id, self.tec_cows)
        self.assertFalse(task.child_ids.portal_user_names, 'by default no user should be assigned to a subtask created by the portal user.')
        self.assertFalse(task.child_ids.user_ids, 'No user should be assigned to the new subtask.')

        task2 = self.env['tec.task'] \
            .with_context({
                'tracking_disable': True,
                'default_tec_id': self.tec_cows.id,
                'default_user_ids': [Command.set(self.user_portal.ids)],
            }) \
            .with_user(self.user_portal) \
            .create({'name': 'Test'})
        self.assertFalse(task2.portal_user_names, 'the portal user should not be assigned when the portal user creates a task into the tec shared.')

        # 3.3) Create a second sub-task
        with self.get_tec_sharing_form_view(task, self.user_portal) as form:
            with form.child_ids.new() as subtask_form:
                subtask_form.name = 'Test Subtask'
        self.assertEqual(len(task.child_ids), 2, 'Check 2 subtasks has correctly been created by the user portal.')

        # Create/Update a forbidden task through child_ids
        with self.assertRaisesRegex(AccessError, "You cannot write on description"):
            task.write({'child_ids': [Command.create({'name': 'Foo', 'description': 'Foo'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            task.write({'child_ids': [Command.update(self.task_no_collabo.id, {'name': 'Foo'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to delete 'Task'"):
            task.write({'child_ids': [Command.delete(self.task_no_collabo.id)]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            task.write({'child_ids': [Command.unlink(self.task_no_collabo.id)]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            task.write({'child_ids': [Command.link(self.task_no_collabo.id)]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Task'"):
            task.write({'child_ids': [Command.set([self.task_no_collabo.id])]})

        # Create/update a tag through tag_ids
        with self.assertRaisesRegex(AccessError, "not allowed to create 'Tec Tags'"):
            task.write({'tag_ids': [Command.create({'name': 'Bar'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to modify 'Tec Tags'"):
            task.write({'tag_ids': [Command.update(self.task_tag.id, {'name': 'Bar'})]})
        with self.assertRaisesRegex(AccessError, "not allowed to delete 'Tec Tags'"):
            task.write({'tag_ids': [Command.delete(self.task_tag.id)]})

        task.write({'tag_ids': [Command.link(self.task_tag.id)]})
        self.assertEqual(task.tag_ids, self.task_tag)

        task.write({'tag_ids': [Command.unlink(self.task_tag.id)]})
        self.assertFalse(task.tag_ids)

        task.write({'tag_ids': [Command.link(self.task_tag.id)]})
        task.write({'tag_ids': [Command.clear()]})
        self.assertFalse(task.tag_ids, [])

        task.write({'tag_ids': [Command.set([self.task_tag.id])]})
        self.assertEqual(task.tag_ids, self.task_tag)


    def test_portal_user_cannot_see_all_assignees(self):
        """ Test when the portal sees a task he cannot see all the assignees.

            Because of a ir.rule in res.partner filters the assignees, the portal
            can only see the assignees in the same company than him.

            Test Cases:
            ==========
            1) add many assignees in a task
            2) check the portal user can read no assignee in this task. Should have an AccessError exception
        """
        self.task_cow.write({'user_ids': [Command.link(self.user_tecmanager.id)]})
        with self.assertRaises(AccessError, msg="Should not accept the portal user to access to a task he does not follow it and its tec."):
            self.task_cow.with_user(self.user_portal).read(['portal_user_names'])
        self.assertEqual(len(self.task_cow.user_ids), 2, '2 users should be assigned in this task.')

        tec_share_wizard = self.env['tec.share.wizard'].create({
            'access_mode': 'edit',
            'res_model': 'tec.tec',
            'res_id': self.tec_cows.id,
            'partner_ids': [
                Command.link(self.user_portal.partner_id.id),
            ],
        })
        tec_share_wizard.action_send_mail()

        self.assertFalse(self.task_cow.with_user(self.user_portal).user_ids, 'the portal user should see no assigness in the task.')
        task_portal_read = self.task_cow.with_user(self.user_portal).read(['portal_user_names'])
        self.assertEqual(self.task_cow.portal_user_names, task_portal_read[0]['portal_user_names'], 'the portal user should see assignees name in the task via the `portal_user_names` field.')

    def test_portal_user_can_change_stage_with_rating(self):
        """ Test portal user can change the stage of task to a stage with rating template email

            The user should be able to change the stage and the email should be sent as expected
            if a email template is set in `rating_template_id` field in the new stage.
        """
        self.tec_portal.write({
            'rating_active': True,
            'rating_status': 'stage',
            'collaborator_ids': [
                Command.create({'partner_id': self.user_portal.partner_id.id}),
            ],
        })
        self.task_portal.with_user(self.user_portal).write({'stage_id': self.tec_portal.type_ids[-1].id})

    def test_orm_method_with_true_false_domain(self):
        """ Test orm method overriden in tec for tec sharing works with TRUE_LEAF/FALSE_LEAF

            Test Case
            =========
            1) Share a tec in edit mode for portal user
            2) Search the portal task contained in the tec shared by using a domain with TRUE_LEAF
            3) Check the task is found with the `search` method
            4) filter the task with `TRUE_DOMAIN` and check if the task is always returned by `filtered_domain` method
            5) filter the task with `FALSE_DOMAIN` and check if no task is returned by `filtered_domain` method
            6) Search the task with `FALSE_LEAF` and check no task is found with `search` method
            7) Call `read_group` method with `TRUE_LEAF` in the domain and check if the task is found
            8) Call `read_group` method with `FALSE_LEAF` in the domain and check if no task is found
        """
        domain = [('id', '=', self.task_portal.id)]
        self.tec_portal.write({
            'collaborator_ids': [Command.create({
                'partner_id': self.user_portal.partner_id.id,
            })],
        })
        task = self.env['tec.task'].with_user(self.user_portal).search(
            expression.AND([
                expression.TRUE_DOMAIN,
                domain,
            ])
        )
        self.assertTrue(task, 'The task should be found.')
        self.assertEqual(task, task.filtered_domain(expression.TRUE_DOMAIN), 'The task found should be kept since the domain is truly')
        self.assertFalse(task.filtered_domain(expression.FALSE_DOMAIN), 'The task should not be found since the domain is falsy')
        task = self.env['tec.task'].with_user(self.user_portal).search(
            expression.AND([
                expression.FALSE_DOMAIN,
                domain,
            ]),
        )
        self.assertFalse(task, 'No task should be found since the domain contained a falsy tuple.')

        task_read_group = self.env['tec.task'].read_group(
            expression.AND([expression.TRUE_DOMAIN, domain]),
            ['id'],
            [],
        )
        self.assertEqual(task_read_group[0]['__count'], 1, 'The task should be found with the read_group method containing a truly tuple.')
        self.assertEqual(task_read_group[0]['id'], self.task_portal.id, 'The task should be found with the read_group method containing a truly tuple.')

        task_read_group = self.env['tec.task'].read_group(
            expression.AND([expression.FALSE_DOMAIN, domain]),
            ['id'],
            [],
        )
        self.assertFalse(task_read_group[0]['__count'], 'No result should found with the read_group since the domain is falsy.')

    def test_milestone_read_access_right(self):
        """ This test ensures that a portal user has read access on the milestone of the tec that was shared with him """

        tec_milestone = self.env['tec.milestone'].create({
            'name': 'Test Tec Milestone',
            'tec_id': self.tec_portal.id,
        })
        with self.assertRaises(AccessError, msg="Should not accept the portal user to access to a milestone if he's not a collaborator of its tec."):
            tec_milestone.with_user(self.user_portal).read(['name'])

        self.tec_portal.write({
            'collaborator_ids': [Command.create({
                'partner_id': self.user_portal.partner_id.id,
            })],
        })
        # Reading the milestone should no longer trigger an access error.
        tec_milestone.with_user(self.user_portal).read(['name'])
        with self.assertRaises(AccessError, msg="Should not accept the portal user to update a milestone."):
            tec_milestone.with_user(self.user_portal).write(['name'])
        with self.assertRaises(AccessError, msg="Should not accept the portal user to delete a milestone."):
            tec_milestone.with_user(self.user_portal).unlink()
        with self.assertRaises(AccessError, msg="Should not accept the portal user to create a milestone."):
            self.env['tec.milestone'].with_user(self.user_portal).create({
                'name': 'Test Tec new Milestone',
                'tec_id': self.tec_portal.id,
            })
