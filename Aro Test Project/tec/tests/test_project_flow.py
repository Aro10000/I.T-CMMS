# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from .test_tec_base import TestTecCommon
from odoo import Command
from odoo.tools import mute_logger
from odoo.addons.mail.tests.common import MailCommon
from odoo.exceptions import AccessError


EMAIL_TPL = """Return-Path: <whatever-2a840@postmaster.twitter.com>
X-Original-To: {to}
Delivered-To: {to}
To: {to}
cc: {cc}
Received: by mail1.odoo.com (Postfix, from userid 10002)
    id 5DF9ABFB2A; Fri, 10 Aug 2012 16:16:39 +0200 (CEST)
Message-ID: {msg_id}
Date: Tue, 29 Nov 2011 12:43:21 +0530
From: {email_from}
MIME-Version: 1.0
Subject: {subject}
Content-Type: text/plain; charset=ISO-8859-1; format=flowed

Hello,

This email should create a new entry in your module. Please check that it
effectively works.

Thanks,

--
Raoul Boitempoils
Integrator at Agrolait"""


class TestTecFlow(TestTecCommon, MailCommon):

    def test_tec_process_tec_manager_duplicate(self):
        pigs = self.tec_pigs.with_user(self.user_tecmanager)
        dogs = pigs.copy()
        self.assertEqual(len(dogs.tasks), 2, 'tec: duplicating a tec must duplicate its tasks')

    @mute_logger('odoo.addons.mail.models.mail_thread')
    def test_task_process_without_stage(self):
        # Do: incoming mail from an unknown partner on an alias creates a new task 'Frogs'
        task = self.format_and_process(
            EMAIL_TPL, to='tec+pigs@mydomain.com, valid.lelitre@agrolait.com', cc='valid.other@gmail.com',
            email_from='%s' % self.user_tecuser.email,
            subject='Frogs', msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
            target_model='tec.task')

        # Test: one task created by mailgateway administrator
        self.assertEqual(len(task), 1, 'tec: message_process: a new tec.task should have been created')
        # Test: check partner in message followers
        self.assertIn(self.partner_2, task.message_partner_ids, "Partner in message cc is not added as a task followers.")
        # Test: messages
        self.assertEqual(len(task.message_ids), 1,
                         'tec: message_process: newly created task should have 1 message: email')
        self.assertEqual(task.message_ids.subtype_id, self.env.ref('tec.mt_task_new'),
                         'tec: message_process: first message of new task should have Task Created subtype')
        self.assertEqual(task.message_ids.author_id, self.user_tecuser.partner_id,
                         'tec: message_process: second message should be the one from Agrolait (partner failed)')
        self.assertEqual(task.message_ids.subject, 'Frogs',
                         'tec: message_process: second message should be the one from Agrolait (subject failed)')
        # Test: task content
        self.assertEqual(task.name, 'Frogs', 'tec_task: name should be the email subject')
        self.assertEqual(task.tec_id, self.tec_pigs, 'tec_task: incorrect tec')
        self.assertEqual(task.stage_id.sequence, False, "tec_task: shouldn't have a stage, i.e. sequence=False")

    @mute_logger('odoo.addons.mail.models.mail_thread')
    def test_task_process_with_stages(self):
        # Do: incoming mail from an unknown partner on an alias creates a new task 'Cats'
        task = self.format_and_process(
            EMAIL_TPL, to='tec+goats@mydomain.com, valid.lelitre@agrolait.com', cc='valid.other@gmail.com',
            email_from='%s' % self.user_tecuser.email,
            subject='Cats', msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
            target_model='tec.task')

        # Test: one task created by mailgateway administrator
        self.assertEqual(len(task), 1, 'tec: message_process: a new tec.task should have been created')
        # Test: check partner in message followers
        self.assertIn(self.partner_2, task.message_partner_ids, "Partner in message cc is not added as a task followers.")
        # Test: messages
        self.assertEqual(len(task.message_ids), 1,
                         'tec: message_process: newly created task should have 1 messages: email')
        self.assertEqual(task.message_ids.subtype_id, self.env.ref('tec.mt_task_new'),
                         'tec: message_process: first message of new task should have Task Created subtype')
        self.assertEqual(task.message_ids.author_id, self.user_tecuser.partner_id,
                         'tec: message_process: first message should be the one from Agrolait (partner failed)')
        self.assertEqual(task.message_ids.subject, 'Cats',
                         'tec: message_process: first message should be the one from Agrolait (subject failed)')
        # Test: task content
        self.assertEqual(task.name, 'Cats', 'tec_task: name should be the email subject')
        self.assertEqual(task.tec_id, self.tec_goats, 'tec_task: incorrect tec')
        self.assertEqual(task.stage_id.sequence, 1, "tec_task: should have a stage with sequence=1")

    @mute_logger('odoo.addons.mail.models.mail_thread')
    def test_task_from_email_alias(self):
        # Do: incoming mail from a known partner email on an alias creates a new task 'Super Frog'
        task = self.format_and_process(
            EMAIL_TPL, to='tec+goats@mydomain.com, valid.lelitre@agrolait.com', cc='valid.other@gmail.com',
            email_from='%s' % self.user_portal.email,
            subject='Super Frog', msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
            target_model='tec.task')

        # Test: one task created by mailgateway administrator
        self.assertEqual(len(task), 1, 'tec: message_process: a new tec.task should have been created')
        # Test: check partner in message followers
        self.assertIn(self.partner_2, task.message_partner_ids, "Partner in message cc is not added as a task followers.")
        # Test: check partner has not been assgined
        self.assertFalse(task.user_ids, "Partner is not added as an assignees")
        # Test: messages
        self.assertEqual(len(task.message_ids), 1,
                         'tec: message_process: newly created task should have 1 messages: email')
        self.assertEqual(task.message_ids.subtype_id, self.env.ref('tec.mt_task_new'),
                         'tec: message_process: first message of new task should have Task Created subtype')
        self.assertEqual(task.message_ids.author_id, self.user_portal.partner_id,
                         'tec: message_process: first message should be the one from Agrolait (partner failed)')
        self.assertEqual(task.message_ids.subject, 'Super Frog',
                         'tec: message_process: first message should be the one from Agrolait (subject failed)')
        # Test: task content
        self.assertEqual(task.name, 'Super Frog', 'tec_task: name should be the email subject')
        self.assertEqual(task.tec_id, self.tec_goats, 'tec_task: incorrect tec')
        self.assertEqual(task.stage_id.sequence, 1, "tec_task: should have a stage with sequence=1")

    def test_subtask_process(self):
        """
        Check subtask mecanism and change it from tec.

        For this test, 2 tecs are used:
            - the 'pigs' tec which has a partner_id
            - the 'goats' tec where the partner_id is removed at the beginning of the tests and then restored.

        2 parent tasks are also used to be able to switch the parent task of a sub-task:
            - 'parent_task' linked to the partner_2
            - 'another_parent_task' linked to the partner_3
        """

        Task = self.env['tec.task'].with_context({'tracking_disable': True})

        parent_task = Task.create({
            'name': 'Mother Task',
            'user_ids': self.user_tecuser,
            'tec_id': self.tec_pigs.id,
            'partner_id': self.partner_2.id,
            'planned_hours': 12,
        })

        another_parent_task = Task.create({
            'name': 'Another Mother Task',
            'user_ids': self.user_tecuser,
            'tec_id': self.tec_pigs.id,
            'partner_id': self.partner_3.id,
            'planned_hours': 0,
        })

        # remove the partner_id of the 'goats' tec
        goats_partner_id = self.tec_goats.partner_id

        self.tec_goats.write({
            'partner_id': False
        })

        # the child task 1 is linked to a tec without partner_id (goats tec)
        child_task_1 = Task.with_context(default_tec_id=self.tec_goats.id, default_parent_id=parent_task.id).create({
            'name': 'Task Child with tec',
            'planned_hours': 3,
        })

        # the child task 2 is linked to a tec with a partner_id (pigs tec)
        child_task_2 = Task.create({
            'name': 'Task Child without tec',
            'parent_id': parent_task.id,
            'tec_id': self.tec_pigs.id,
            'display_tec_id': self.tec_pigs.id,
            'planned_hours': 5,
        })

        self.assertEqual(
            child_task_1.partner_id, child_task_1.parent_id.partner_id,
            "When no tec partner_id has been set, a subtask should have the same partner as its parent")

        self.assertEqual(
            child_task_2.partner_id, child_task_2.parent_id.partner_id,
            "When a tec partner_id has been set, a subtask should have the same partner as its parent")

        self.assertEqual(
            parent_task.subtask_count, 2,
            "Parent task should have 2 children")

        self.assertEqual(
            parent_task.subtask_planned_hours, 8,
            "Planned hours of subtask should impact parent task")

        # change the parent of a subtask without a tec partner_id
        child_task_1.write({
            'parent_id': another_parent_task.id
        })

        self.assertEqual(
            child_task_1.partner_id, parent_task.partner_id,
            "When changing the parent task of a subtask with no tec partner_id, the partner_id should remain the same.")

        # change the parent of a subtask with a tec partner_id
        child_task_2.write({
            'parent_id': another_parent_task.id
        })

        self.assertEqual(
            child_task_2.partner_id, parent_task.partner_id,
            "When changing the parent task of a subtask with a tec, the partner_id should remain the same.")

        # set a tec with partner_id to a subtask without tec partner_id
        child_task_1.write({
            'display_tec_id': self.tec_pigs.id
        })

        self.assertNotEqual(
            child_task_1.partner_id, self.tec_pigs.partner_id,
            "When the tec changes, the subtask should keep its partner id as its partner id is set.")

        # restore the partner_id of the 'goats' tec
        self.tec_goats.write({
            'partner_id': goats_partner_id
        })

        # set a tec with partner_id to a subtask with a tec partner_id
        child_task_2.write({
            'display_tec_id': self.tec_goats.id
        })

        self.assertEqual(
            child_task_2.partner_id, parent_task.partner_id,
            "When the tec changes, the subtask should keep the same partner id even it has a new tec.")

    def test_rating(self):
        """Check if rating works correctly even when task is changed from tec A to tec B"""
        Task = self.env['tec.task'].with_context({'tracking_disable': True})
        first_task = Task.create({
            'name': 'first task',
            'user_ids': self.user_tecuser,
            'tec_id': self.tec_pigs.id,
            'partner_id': self.partner_2.id,
        })

        self.assertEqual(first_task.rating_count, 0, "Task should have no rating associated with it")

        rating_good = self.env['rating.rating'].create({
            'res_model_id': self.env['ir.model']._get('tec.task').id,
            'res_id': first_task.id,
            'parent_res_model_id': self.env['ir.model']._get('tec.tec').id,
            'parent_res_id': self.tec_pigs.id,
            'rated_partner_id': self.partner_2.id,
            'partner_id': self.partner_2.id,
            'rating': 5,
            'consumed': False,
        })

        rating_bad = self.env['rating.rating'].create({
            'res_model_id': self.env['ir.model']._get('tec.task').id,
            'res_id': first_task.id,
            'parent_res_model_id': self.env['ir.model']._get('tec.tec').id,
            'parent_res_id': self.tec_pigs.id,
            'rated_partner_id': self.partner_2.id,
            'partner_id': self.partner_2.id,
            'rating': 3,
            'consumed': True,
        })

        # We need to invalidate cache since it is not done automatically by the ORM
        # Our One2Many is linked to a res_id (int) for which the orm doesn't create an inverse
        self.env.invalidate_all()

        self.assertEqual(rating_good.rating_text, 'top')
        self.assertEqual(rating_bad.rating_text, 'ok')
        self.assertEqual(first_task.rating_count, 1, "Task should have only one rating associated, since one is not consumed")
        self.assertEqual(rating_good.parent_res_id, self.tec_pigs.id)

        self.assertEqual(self.tec_goats.rating_percentage_satisfaction, -1)
        self.assertEqual(self.tec_goats.rating_avg, 0, 'Since there is no rating in this tec, the Average Rating should be equal to 0.')
        self.assertEqual(self.tec_pigs.rating_percentage_satisfaction, 0)  # There is a rating but not a "great" on, just an "okay".
        self.assertEqual(self.tec_pigs.rating_avg, rating_bad.rating, 'Since there is only one rating the Average Rating should be equal to the rating value of this one.')

        # Consuming rating_good
        first_task.rating_apply(5, rating_good.access_token)

        # We need to invalidate cache since it is not done automatically by the ORM
        # Our One2Many is linked to a res_id (int) for which the orm doesn't create an inverse
        self.env.invalidate_all()

        rating_avg = (rating_good.rating + rating_bad.rating) / 2
        self.assertEqual(first_task.rating_count, 2, "Task should have two ratings associated with it")
        self.assertEqual(first_task.rating_avg_text, 'top')
        self.assertEqual(rating_good.parent_res_id, self.tec_pigs.id)
        self.assertEqual(self.tec_goats.rating_percentage_satisfaction, -1)
        self.assertEqual(self.tec_pigs.rating_percentage_satisfaction, 50)
        self.assertEqual(self.tec_pigs.rating_avg, rating_avg)
        self.assertEqual(self.tec_pigs.rating_avg_percentage, rating_avg / 5)

        # We change the task from tec_pigs to tec_goats, ratings should be associated with the new tec
        first_task.tec_id = self.tec_goats.id

        # We need to invalidate cache since it is not done automatically by the ORM
        # Our One2Many is linked to a res_id (int) for which the orm doesn't create an inverse
        self.env.invalidate_all()

        self.assertEqual(rating_good.parent_res_id, self.tec_goats.id)
        self.assertEqual(self.tec_goats.rating_percentage_satisfaction, 50)
        self.assertEqual(self.tec_goats.rating_avg, rating_avg)
        self.assertEqual(self.tec_pigs.rating_percentage_satisfaction, -1)
        self.assertEqual(self.tec_pigs.rating_avg, 0)

    def test_task_with_no_tec(self):
        """
            With this test, we want to make sure the fact that a task has no tec doesn't affect the entire
            behaviours of tecs.

            1) Try to compute every field of a task which has no tec.
            2) Try to compute every field of a tec and assert it isn't affected by this use case.
        """
        task_without_tec = self.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test task without tec'
        })

        for field in task_without_tec._fields.keys():
            try:
                task_without_tec[field]
            except Exception as e:
                raise AssertionError("Error raised unexpectedly while computing a field of the task ! Exception : " + e.args[0])

        for field in self.tec_pigs._fields.keys():
            try:
                self.tec_pigs[field]
            except Exception as e:
                raise AssertionError("Error raised unexpectedly while computing a field of the tec ! Exception : " + e.args[0])

        # tasks with no tec set should only be visible to the users assigned to them
        task_without_tec.user_ids = [Command.link(self.user_tecuser.id)]
        task_without_tec.with_user(self.user_tecuser).read(['name'])
        with self.assertRaises(AccessError):
            task_without_tec.with_user(self.user_tecmanager).read(['name'])

        # Tests that tasks assigned to the current user should be in the right default stage
        task = self.env['tec.task'].create({
            'name': 'Test Task!',
            'user_ids': [Command.link(self.env.user.id)],
        })
        stages = task._get_default_personal_stage_create_vals(self.env.user.id)
        self.assertEqual(task.personal_stage_id.stage_id.name, stages[0].get('name'), "tasks assigned to the current user should be in the right default stage")

    def test_send_rating_review(self):
        tec_settings = self.env["res.config.settings"].create({'group_tec_rating': True})
        tec_settings.execute()
        self.assertTrue(self.tec_goats.rating_active, 'The customer ratings should be enabled in this tec.')

        won_stage = self.tec_goats.type_ids[-1]
        rating_request_mail_template = self.env.ref('tec.rating_tec_request_email_template')
        won_stage.write({'rating_template_id': rating_request_mail_template.id})
        tasks = self.env['tec.task'].with_context(mail_create_nolog=True, default_tec_id=self.tec_goats.id).create([
            {'name': 'Goat Task 1', 'user_ids': [Command.set([])]},
            {'name': 'Goat Task 2', 'user_ids': [Command.link(self.user_tecuser.id)]},
            {
                'name': 'Goat Task 3',
                'user_ids': [
                    Command.link(self.user_tecmanager.id),
                    Command.link(self.user_tecuser.id),
                ],
            },
        ])

        with self.mock_mail_gateway():
            tasks.with_user(self.user_tecmanager).write({'stage_id': won_stage.id})

        tasks.invalidate_model(['rating_ids'])
        for task in tasks:
            self.assertEqual(len(task.rating_ids), 1, 'This task should have a generated rating when it arrives in the Won stage.')
            rating_request_message = task.message_ids[:1]
            if not task.user_ids or len(task.user_ids) > 1:
                self.assertFalse(task.rating_ids.rated_partner_id, 'This rating should have no assigned user if the task related have no assignees or more than one assignee.')
                self.assertEqual(rating_request_message.email_from, self.user_tecmanager.partner_id.email_formatted, 'The message should have the email of the Tec Manager as email from.')
            else:
                self.assertEqual(task.rating_ids.rated_partner_id, task.user_ids.partner_id, 'The rating should have an assigned user if the task has only one assignee.')
                self.assertEqual(rating_request_message.email_from, task.user_ids.partner_id.email_formatted, 'The message should have the email of the assigned user in the task as email from.')
            self.assertTrue(self.partner_1 in rating_request_message.partner_ids, 'The customer of the task should be in the partner_ids of the rating request message.')

    def test_email_track_template(self):
        """ Update some tracked fields linked to some template -> message with onchange """
        tec_settings = self.env["res.config.settings"].create({'group_tec_stages': True})
        tec_settings.execute()

        mail_template = self.env['mail.template'].create({
            'name': 'Test template',
            'subject': 'Test',
            'body_html': '<p>Test</p>',
            'auto_delete': True,
            'model_id': self.env.ref('tec.model_tec_tec_stage').id,
        })
        tec_A = self.env['tec.tec'].create({
            'name': 'tec_A',
            'privacy_visibility': 'followers',
            'alias_name': 'tec A',
            'partner_id': self.partner_1.id,
        })
        init_stage = tec_A.stage_id.name

        tec_stage = self.env.ref('tec.tec_tec_stage_1')
        self.assertNotEqual(tec_A.stage_id, tec_stage)

        # Assign email template
        tec_stage.mail_template_id = mail_template.id
        self.flush_tracking()
        init_nb_log = len(tec_A.message_ids)
        tec_A.stage_id = tec_stage.id
        self.flush_tracking()
        self.assertNotEqual(init_stage, tec_A.stage_id.name)

        self.assertEqual(len(tec_A.message_ids), init_nb_log + 2,
            "should have 2 new messages: one for tracking, one for template")

    def test_private_task_search_tag(self):
        task = self.env['tec.task'].create({
            'name': 'Test Private Task',
        })
        # Tag name_search should not raise Error if tec_id is False
        task.tag_ids.with_context(tec_id=task.tec_id.id).name_search(
            args=["!", ["id", "in", []]])
