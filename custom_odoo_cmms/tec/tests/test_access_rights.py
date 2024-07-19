# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.tec.tests.test_tec_base import TestTecCommon
from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import users
from odoo.tools import mute_logger

class TestAccessRights(TestTecCommon):
    def setUp(self):
        super().setUp()
        self.task = self.create_task('Make the world a better place')
        self.user = mail_new_test_user(self.env, 'Internal user', groups='base.group_user')
        self.portal = mail_new_test_user(self.env, 'Portal user', groups='base.group_portal')

    def create_task(self, name, *, with_user=None, **kwargs):
        values = dict(name=name, tec_id=self.tec_pigs.id, **kwargs)
        return self.env['tec.task'].with_user(with_user or self.env.user).create(values)

class TestCRUDVisibilityFollowers(TestAccessRights):

    def setUp(self):
        super().setUp()
        self.tec_pigs.privacy_visibility = 'followers'

    @users('Internal user', 'Portal user')
    def test_tec_no_write(self):
        with self.assertRaises(AccessError, msg="%s should not be able to write on the tec" % self.env.user.name):
            self.tec_pigs.with_user(self.env.user).name = "Take over the world"

        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        with self.assertRaises(AccessError, msg="%s should not be able to write on the tec" % self.env.user.name):
            self.tec_pigs.with_user(self.env.user).name = "Take over the world"

    @users('Internal user', 'Portal user')
    def test_tec_no_unlink(self):
        self.tec_pigs.task_ids.unlink()
        with self.assertRaises(AccessError, msg="%s should not be able to unlink the tec" % self.env.user.name):
            self.tec_pigs.with_user(self.env.user).unlink()

        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        self.tec_pigs.task_ids.unlink()
        with self.assertRaises(AccessError, msg="%s should not be able to unlink the tec" % self.env.user.name):
            self.tec_pigs.with_user(self.env.user).unlink()

    @users('Internal user', 'Portal user')
    def test_tec_no_read(self):
        with self.assertRaises(AccessError, msg="%s should not be able to read the tec" % self.env.user.name):
            self.tec_pigs.with_user(self.env.user).name

    @users('Portal user')
    def test_tec_allowed_portal_no_read(self):
        self.tec_pigs.privacy_visibility = 'portal'
        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        self.tec_pigs.privacy_visibility = 'followers'
        with self.assertRaises(AccessError, msg="%s should not be able to read the tec" % self.env.user.name):
            self.tec_pigs.with_user(self.env.user).name

    @users('Internal user')
    def test_tec_allowed_internal_read(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        self.tec_pigs.flush_model()
        self.tec_pigs.invalidate_model()
        self.tec_pigs.with_user(self.env.user).name

    @users('Internal user', 'Portal user')
    def test_task_no_read(self):
        with self.assertRaises(AccessError, msg="%s should not be able to read the task" % self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Portal user')
    def test_task_allowed_portal_no_read(self):
        self.tec_pigs.privacy_visibility = 'portal'
        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        self.tec_pigs.privacy_visibility = 'followers'
        with self.assertRaises(AccessError, msg="%s should not be able to read the task" % self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Internal user')
    def test_task_allowed_internal_read(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        self.task.flush_model()
        self.task.invalidate_model()
        self.task.with_user(self.env.user).name

    @users('Internal user', 'Portal user')
    def test_task_no_write(self):
        with self.assertRaises(AccessError, msg="%s should not be able to write on the task" % self.env.user.name):
            self.task.with_user(self.env.user).name = "Paint the world in black & white"

        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        with self.assertRaises(AccessError, msg="%s should not be able to write on the task" % self.env.user.name):
            self.task.with_user(self.env.user).name = "Paint the world in black & white"

    @users('Internal user', 'Portal user')
    def test_task_no_create(self):
        with self.assertRaises(AccessError, msg="%s should not be able to create a task" % self.env.user.name):
            self.create_task("Archive the world, it's not needed anymore")

        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        with self.assertRaises(AccessError, msg="%s should not be able to create a task" % self.env.user.name):
            self.create_task("Archive the world, it's not needed anymore")

    @users('Internal user', 'Portal user')
    def test_task_no_unlink(self):
        with self.assertRaises(AccessError, msg="%s should not be able to unlink the task" % self.env.user.name):
            self.task.with_user(self.env.user).unlink()

        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        with self.assertRaises(AccessError, msg="%s should not be able to unlink the task" % self.env.user.name):
            self.task.with_user(self.env.user).unlink()

class TestCRUDVisibilityPortal(TestAccessRights):

    def setUp(self):
        super().setUp()
        self.tec_pigs.privacy_visibility = 'portal'
        self.env.flush_all()

    @users('Portal user')
    def test_task_portal_no_read(self):
        with self.assertRaises(AccessError, msg="%s should not be able to read the task" % self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Portal user')
    def test_task_allowed_portal_read(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        self.task.flush_model()
        self.task.invalidate_model()
        self.task.with_user(self.env.user).name

    @users('Internal user')
    def test_task_internal_read(self):
        self.task.flush_model()
        self.task.invalidate_model()
        self.task.with_user(self.env.user).name

class TestCRUDVisibilityEmployees(TestAccessRights):

    def setUp(self):
        super().setUp()
        self.tec_pigs.privacy_visibility = 'employees'

    @users('Portal user')
    def test_task_portal_no_read(self):
        with self.assertRaises(AccessError, msg="%s should not be able to read the task" % self.env.user.name):
            self.task.with_user(self.env.user).name

        self.tec_pigs.message_subscribe(partner_ids=[self.env.user.partner_id.id])
        with self.assertRaises(AccessError, msg="%s should not be able to read the task" % self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Internal user')
    def test_task_allowed_portal_read(self):
        self.task.flush_model()
        self.task.invalidate_model()
        self.task.with_user(self.env.user).name

class TestAllowedUsers(TestAccessRights):

    def setUp(self):
        super().setUp()
        self.tec_pigs.privacy_visibility = 'followers'

    def test_tec_permission_added(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.user.partner_id.id])
        self.assertIn(self.user.partner_id, self.tec_pigs.message_partner_ids)
        # Subscribing to a tec should not cause subscription to existing tasks in the tec.
        self.assertNotIn(self.user.partner_id, self.task.message_partner_ids)

    def test_tec_default_permission(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.user.partner_id.id])
        created_task = self.create_task("Review the end of the world")
        # Subscribing to a tec should cause subscription to new tasks in the tec.
        self.assertIn(self.user.partner_id, created_task.message_partner_ids)

    def test_tec_default_customer_permission(self):
        self.tec_pigs.privacy_visibility = 'portal'
        self.tec_pigs.message_subscribe(partner_ids=[self.portal.partner_id.id])
        # Subscribing a default customer to a tec should not cause its subscription to existing tasks in the tec.
        self.assertNotIn(self.portal.partner_id, self.task.message_partner_ids)
        self.assertIn(self.portal.partner_id, self.tec_pigs.message_partner_ids)

    def test_tec_permission_removed(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.user.partner_id.id])
        self.tec_pigs.message_unsubscribe(partner_ids=[self.user.partner_id.id])
        # Unsubscribing to a tec should not cause unsubscription of existing tasks in the tec.
        self.assertNotIn(self.user.partner_id, self.tec_pigs.message_partner_ids)

    def test_tec_specific_permission(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.user.partner_id.id])
        john = mail_new_test_user(self.env, 'John')
        self.tec_pigs.message_subscribe(partner_ids=[john.partner_id.id])
        self.tec_pigs.message_unsubscribe(partner_ids=[self.user.partner_id.id])
        # User specific subscribing to a tec should not cause its subscription to existing tasks in the tec.
        self.assertNotIn(john.partner_id, self.task.message_partner_ids, "John should not be allowed to read the task")
        task = self.create_task("New task")
        self.assertIn(john.partner_id, task.message_partner_ids, "John should allowed to read the task")

    def test_tec_specific_remove_mutliple_tasks(self):
        self.tec_pigs.message_subscribe(partner_ids=[self.user.partner_id.id])
        john = mail_new_test_user(self.env, 'John')
        task = self.create_task('task')
        self.task.message_subscribe(partner_ids=[john.partner_id.id])
        self.tec_pigs.message_unsubscribe(partner_ids=[self.user.partner_id.id])
        self.assertIn(john.partner_id, self.task.message_partner_ids)
        self.assertNotIn(john.partner_id, task.message_partner_ids)
        # Unsubscribing to a tec should not cause unsubscription of existing tasks in the tec.
        self.assertIn(self.user.partner_id, task.message_partner_ids)
        self.assertNotIn(self.user.partner_id, self.task.message_partner_ids)

    def test_visibility_changed(self):
        self.tec_pigs.privacy_visibility = 'portal'
        self.task.message_subscribe(partner_ids=[self.portal.partner_id.id])
        self.assertNotIn(self.user.partner_id, self.task.message_partner_ids, "Internal user should have been removed from allowed users")
        self.tec_pigs.write({'privacy_visibility': 'employees'})
        self.assertNotIn(self.portal.partner_id, self.task.message_partner_ids, "Portal user should have been removed from allowed users")

    def test_write_task(self):
        self.user.groups_id |= self.env.ref('tec.group_tec_user')
        self.assertNotIn(self.user.partner_id, self.tec_pigs.message_partner_ids)
        self.task.message_subscribe(partner_ids=[self.user.partner_id.id])
        self.tec_pigs.invalidate_model()
        self.task.invalidate_model()
        self.task.with_user(self.user).name = "I can edit a task!"

    def test_no_write_tec(self):
        self.user.groups_id |= self.env.ref('tec.group_tec_user')
        self.assertNotIn(self.user.partner_id, self.tec_pigs.message_partner_ids)
        with self.assertRaises(AccessError, msg="User should not be able to edit tec"):
            self.tec_pigs.with_user(self.user).name = "I can't edit a task!"

class TestTecPortalCommon(TestTecCommon):

    def setUp(self):
        super(TestTecPortalCommon, self).setUp()
        self.user_noone = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'Noemie NoOne',
            'login': 'noemie',
            'email': 'n.n@example.com',
            'signature': '--\nNoemie',
            'notification_type': 'email',
            'groups_id': [(6, 0, [])]})

        self.task_3 = self.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test3', 'user_ids': self.user_portal, 'tec_id': self.tec_pigs.id})
        self.task_4 = self.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test4', 'user_ids': self.user_public, 'tec_id': self.tec_pigs.id})
        self.task_5 = self.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_ids': False, 'tec_id': self.tec_pigs.id})
        self.task_6 = self.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_ids': False, 'tec_id': self.tec_pigs.id})

class TestPortalTec(TestTecPortalCommon):

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_employee_tec_access_rights(self):
        pigs = self.tec_pigs

        pigs.write({'privacy_visibility': 'employees'})
        # Do: Alfred reads tec -> ok (employee ok employee)
        pigs.with_user(self.user_tecuser).read(['user_id'])
        # Test: all tec tasks visible
        tasks = self.env['tec.task'].with_user(self.user_tecuser).search([('tec_id', '=', pigs.id)])
        test_task_ids = set([self.task_1.id, self.task_2.id, self.task_3.id, self.task_4.id, self.task_5.id, self.task_6.id])
        self.assertEqual(set(tasks.ids), test_task_ids,
                         'access rights: tec user cannot see all tasks of an employees tec')
        # Do: Bert reads tec -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])
        # Do: Donovan reads tec -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: tec user is employee and can create a task
        tmp_task = self.env['tec.task'].with_user(self.user_tecuser).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task',
            'tec_id': pigs.id})
        tmp_task.with_user(self.user_tecuser).unlink()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_favorite_tec_access_rights(self):
        pigs = self.tec_pigs.with_user(self.user_tecuser)

        # we can't write on tec name
        self.assertRaises(AccessError, pigs.write, {'name': 'False Pigs'})
        # we can write on is_favorite
        pigs.write({'is_favorite': True})

    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_followers_tec_access_rights(self):
        pigs = self.tec_pigs
        pigs.write({'privacy_visibility': 'followers'})
        # Do: Alfred reads tec -> ko (employee ko followers)
        self.assertRaises(AccessError, pigs.with_user(self.user_tecuser).read, ['user_id'])
        # Test: no tec task visible
        tasks = self.env['tec.task'].with_user(self.user_tecuser).search([('tec_id', '=', pigs.id)])
        self.assertEqual(tasks, self.task_1,
                         'access rights: employee user should not see tasks of a not-followed followers tec, only assigned')

        # Do: Bert reads tec -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])

        # Do: Donovan reads tec -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])

        pigs.message_subscribe(partner_ids=[self.user_tecuser.partner_id.id])

        # Do: Alfred reads tec -> ok (follower ok followers)
        donkey = pigs.with_user(self.user_tecuser)
        donkey.invalidate_model()
        donkey.read(['user_id'])

        # Do: Donovan reads tec -> ko (public ko follower even if follower)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: tec user is follower of the tec and can create a task
        self.env['tec.task'].with_user(self.user_tecuser).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task', 'tec_id': pigs.id
        })
        # not follower user should not be able to create a task
        pigs.with_user(self.user_tecuser).message_unsubscribe(partner_ids=[self.user_tecuser.partner_id.id])
        self.assertRaises(AccessError, self.env['tec.task'].with_user(self.user_tecuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'tec_id': pigs.id})

        # Do: tec user can create a task without tec
        self.assertRaises(AccessError, self.env['tec.task'].with_user(self.user_tecuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'tec_id': pigs.id})


class TestAccessRightsPrivateTask(TestAccessRights):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_task = cls.env['tec.task'].create({'name': 'OdooBot Private Task'})

    def setUp(self):
        super().setUp()
        self.tec_user = mail_new_test_user(self.env, 'Tec user', groups='tec.group_tec_user')

    def create_private_task(self, name, with_user=None, **kwargs):
        user = with_user or self.env.user
        values = {'name': name, 'user_ids': [Command.set(user.ids)], **kwargs}
        return self.env['tec.task'].with_user(user).create(values)

    @users('Internal user', 'Portal user')
    def test_internal_cannot_crud_private_task(self):
        with self.assertRaises(AccessError):
            self.create_private_task('Private task')

        with self.assertRaises(AccessError):
            self.private_task.with_user(self.env.user).write({'name': 'Test write'})

        with self.assertRaises(AccessError):
            self.private_task.with_user(self.env.user).unlink()

        with self.assertRaises(AccessError):
            self.private_task.with_user(self.env.user).read(['name'])

    @users('Tec user')
    def test_tec_user_crud_own_private_task(self):
        private_task = self.create_private_task('Private task')

        private_task.with_user(self.env.user).write({'name': 'Test write'})
        vals = private_task.with_user(self.env.user).read(['name'])
        self.assertEqual(vals[0]['id'], private_task.id)
        self.assertEqual(vals[0]['name'], private_task.name)

    @users('Tec user')
    def test_tec_user_can_create_private_task_for_another_user(self):
        self.create_private_task('Private task', user_ids=[Command.set(self.user_tecuser.ids)])

    @users('Tec user')
    def test_tec_current_user_is_added_in_private_task_assignees(self):
        task_values = {'name': 'Private task'}
        my_private_task = self.env['tec.task'].create(task_values)
        self.assertEqual(my_private_task.user_ids, self.env.user, 'When no assignee is set on a private task, the task should be assigned to the current user.')
        user_tecuser_private_task = self.env['tec.task'].create({**task_values, 'user_ids': [Command.set(self.user_tecuser.ids)]})
        self.assertTrue(self.env.user in user_tecuser_private_task.user_ids, 'When creating a private task for another user, the current user should be added to the assignees.')

    @users('Tec user')
    def test_tec_current_user_is_added_in_task_assignees_when_tec_id_is_set(self):
        task_values = {'name': 'Private task', 'tec_id': self.tec_pigs.id, 'user_ids': [Command.set(self.user_tecuser.ids)]}
        user_tecuser_task = self.env['tec.task'].create(task_values)
        self.assertFalse(self.env.user in user_tecuser_task.user_ids, "When creating a task that has a tec for another user, the current user should not be added to the assignees.")

    @users('Tec user')
    def test_tec_current_user_is_set_as_assignee_in_task_when_tec_id_is_set_with_no_assignees(self):
        task = self.env['tec.task'].create({'name': 'Private task', 'tec_id': self.tec_pigs.id})
        self.assertEqual(task.user_ids, self.env.user, "When creating a task that has a tec without assignees, the task will be assigned to the current user if no default_tec_id is provided in the context (which is handled in _default_personal_stage_type_id).")

    @users('Tec user')
    def test_tec_current_user_is_not_added_in_private_task_assignees_when_default_tec_id_is_in_the_context(self):
        task_values = {'name': 'Private task'}
        context = {'default_tec_id': self.tec_pigs.id}
        TecTask_with_default_tec_id = self.env['tec.task'].with_context(context)
        task = TecTask_with_default_tec_id.create(task_values)
        self.assertNotEqual(task.user_ids, self.env.user, "When creating a task without assignees and providing default_tec_id in the context, the task should not be assigned to the current user.")
        user_tecuser_task = TecTask_with_default_tec_id.create({**task_values, 'user_ids': [Command.set(self.user_tecuser.ids)]})
        self.assertFalse(self.env.user in user_tecuser_task.user_ids, "When creating a task for another user and providing default_tec_id in the context, the current user should not be added to the assignees.")

    @users('Tec user')
    def test_tec_user_cannot_write_private_task_of_another_user(self):
        with self.assertRaises(AccessError):
            self.private_task.with_user(self.env.user).write({'name': 'Test write'})

    @users('Tec user')
    def test_tec_user_cannot_read_private_task_of_another_user(self):
        with self.assertRaises(AccessError):
            self.private_task.with_user(self.env.user).read(['name'])

    @users('Tec user')
    def test_tec_user_cannot_unlink_private_task_of_another_user(self):
        with self.assertRaises(AccessError):
            self.private_task.with_user(self.env.user).unlink()

    def test_of_setting_root_user_on_private_task(self):
        test_task = self.env['tec.task'].create({
            'name':'Test Private Task',
            'user_ids': [Command.link(self.user_tecuser.id)]
        })
        self.assertNotEqual(test_task.user_ids, self.env.user, "Created private task should not have odoobot as asignee")
