# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from .test_tec_base import TestTecCommon

class TestTaskFollow(TestTecCommon):

    def test_follow_on_create(self):
        # Tests that the user is follower of the task upon creation
        self.assertTrue(self.user_tecuser.partner_id in self.task_1.message_partner_ids)

    def test_follow_on_write(self):
        # Tests that the user is follower of the task upon writing new assignees
        self.task_2.user_ids += self.user_tecmanager
        self.assertTrue(self.user_tecmanager.partner_id in self.task_2.message_partner_ids)
