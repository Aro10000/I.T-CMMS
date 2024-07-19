# -*- coding: utf-8 -*-
import json

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestTecCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestTecCommon, cls).setUpClass()

        user_group_employee = cls.env.ref('base.group_user')
        user_group_tec_user = cls.env.ref('tec.group_tec_user')
        user_group_tec_manager = cls.env.ref('tec.group_tec_manager')

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Valid Lelitre',
            'email': 'valid.lelitre@agrolait.com'})
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Valid Poilvache',
            'email': 'valid.other@gmail.com'})
        cls.partner_3 = cls.env['res.partner'].create({
            'name': 'Valid Poilboeuf',
            'email': 'valid.poilboeuf@gmail.com'})

        # Test users to use through the various tests
        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user_public = Users.create({
            'name': 'Bert Tartignole',
            'login': 'bert',
            'email': 'b.t@example.com',
            'signature': 'SignBert',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_public').id])]})
        cls.user_portal = Users.create({
            'name': 'Chell Gladys',
            'login': 'chell',
            'email': 'chell@gladys.portal',
            'signature': 'SignChell',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]})
        cls.user_tecuser = Users.create({
            'name': 'Armande TecUser',
            'login': 'armandel',
            'password': 'armandel',
            'email': 'armande.tecuser@example.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_tec_user.id])]
        })
        cls.user_tecmanager = Users.create({
            'name': 'Bastien TecManager',
            'login': 'bastien',
            'email': 'bastien.tecmanager@example.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_tec_manager.id])]})

        # Test 'Pigs' tec
        cls.tec_pigs = cls.env['tec.tec'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs',
            'privacy_visibility': 'employees',
            'alias_name': 'tec+pigs',
            'partner_id': cls.partner_1.id})
        # Already-existing tasks in Pigs
        cls.task_1 = cls.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs UserTask',
            'user_ids': cls.user_tecuser,
            'tec_id': cls.tec_pigs.id})
        cls.task_2 = cls.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs ManagerTask',
            'user_ids': cls.user_tecmanager,
            'tec_id': cls.tec_pigs.id})

        # Test 'Goats' tec, same as 'Pigs', but with 2 stages
        cls.tec_goats = cls.env['tec.tec'].with_context({'mail_create_nolog': True}).create({
            'name': 'Goats',
            'privacy_visibility': 'followers',
            'alias_name': 'tec+goats',
            'partner_id': cls.partner_1.id,
            'type_ids': [
                (0, 0, {
                    'name': 'New',
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': 'Won',
                    'sequence': 10,
                })]
            })

    def format_and_process(self, template, to='groups@example.com, other@gmail.com', subject='Frogs',
                           extra='', email_from='Sylvie Lelitre <test.sylvie.lelitre@agrolait.com>',
                           cc='', msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
                           model=None, target_model='tec.task', target_field='name'):
        self.assertFalse(self.env[target_model].search([(target_field, '=', subject)]))
        mail = template.format(to=to, subject=subject, cc=cc, extra=extra, email_from=email_from, msg_id=msg_id)
        self.env['mail.thread'].message_process(model, mail)
        return self.env[target_model].search([(target_field, '=', subject)])


class TestTecBase(TestTecCommon):

    def test_delete_tec_with_tasks(self):
        """Test all tasks linked to a tec are removed when the user removes this tec. """
        task_type = self.env['tec.task.type'].create({'name': 'Won', 'sequence': 1, 'fold': True})
        tec_unlink = self.env['tec.tec'].with_context({'mail_create_nolog': True}).create({
            'name': 'rev',
            'privacy_visibility': 'employees',
            'alias_name': 'rev',
            'partner_id': self.partner_1.id,
            'type_ids': task_type,
        })

        self.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs UserTask',
            'user_ids': self.user_tecuser,
            'tec_id': tec_unlink.id,
            'stage_id': task_type.id})

        task_count = len(tec_unlink.tasks)
        self.assertEqual(task_count, 1, "The tec should have 1 task")

        tec_unlink.unlink()
        self.assertNotEqual(task_count, 0, "The all tasks linked to tec should be deleted when user delete the tec")

    def test_auto_assign_stages_when_importing_tasks(self):
        self.assertFalse(self.tec_pigs.type_ids)
        self.assertEqual(len(self.tec_goats.type_ids), 2)
        first_stage = self.tec_goats.type_ids[0]
        self.env['tec.task']._load_records_create([{
            'name': 'First Task',
            'tec_id': self.tec_pigs.id,
            'stage_id': first_stage.id,
        }])
        self.assertEqual(self.tec_pigs.type_ids, first_stage)
        self.env['tec.task']._load_records_create([
            {
                'name': 'task',
                'tec_id': self.tec_pigs.id,
                'stage_id': stage.id,
            } for stage in self.tec_goats.type_ids
        ])
        self.assertEqual(self.tec_pigs.type_ids, self.tec_goats.type_ids)

    def test_filter_visibility_unread_messages(self):
        """Tests the visibility of the "Unread messages" filter in the tec task search view
        according to the notification type of the user.
        A user with the email notification type must not see the Unread messages filter
        A user with the inbox notification type must see the Unread messages filter"""
        user1 = self.user_tecuser
        user2 = self.user_tecuser.copy()
        user1.notification_type = 'email'
        user2.notification_type = 'inbox'
        for user, filter_invisible_expected in ((user1, True), (user2, None)):
            Task = self.env['tec.task'].with_user(user)
            arch = Task.get_view(self.env.ref('tec.view_task_search_form').id, 'search')['arch']
            tree = etree.fromstring(arch)
            node = tree.xpath('//filter[@name="message_needaction"]')[0]
            modifiers = json.loads(node.get('modifiers') or '{}')
            self.assertEqual(modifiers.get('invisible'), filter_invisible_expected)
