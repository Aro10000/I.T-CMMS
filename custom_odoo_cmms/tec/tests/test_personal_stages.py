# -*- coding: utf-8 -*-

from odoo.tests import tagged, HttpCase

from .test_tec_base import TestTecCommon

@tagged('-at_install', 'post_install', 'personal_stages')
class TestPersonalStages(TestTecCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_stages = cls.env['tec.task.type'].search([('user_id', '=', cls.user_tecuser.id)])
        cls.manager_stages = cls.env['tec.task.type'].search([('user_id', '=', cls.user_tecmanager.id)])

    def test_personal_stage_base(self):
        # Tec User is assigned to task_1 he should be able to see a personal stage
        self.task_1.with_user(self.user_tecuser)._compute_personal_stage_id()
        self.assertTrue(self.task_1.with_user(self.user_tecuser).personal_stage_type_id,
            'Tec User is assigned to task 1, he should have a personal stage assigned.')

        self.task_1.with_user(self.user_tecmanager)._compute_personal_stage_id()
        self.assertFalse(self.env['tec.task'].browse(self.task_1.id).with_user(self.user_tecmanager).personal_stage_type_id,
            'Tec Manager is not assigned to task 1, he should not have a personal stage assigned.')

        # Now assign a second user to our task_1
        self.task_1.user_ids += self.user_tecmanager
        self.assertTrue(self.task_1.with_user(self.user_tecmanager).personal_stage_type_id,
            'Tec Manager has now been assigned to task 1 and should have a personal stage assigned.')

        self.task_1.with_user(self.user_tecmanager)._compute_personal_stage_id()
        task_1_manager_stage = self.task_1.with_user(self.user_tecmanager).personal_stage_type_id

        self.task_1.with_user(self.user_tecuser)._compute_personal_stage_id()
        self.task_1.with_user(self.user_tecuser).personal_stage_type_id = self.user_stages[1]
        self.assertEqual(self.task_1.with_user(self.user_tecuser).personal_stage_type_id, self.user_stages[1],
            'Assigning another personal stage to the task should have changed it for user 1.')

        self.task_1.with_user(self.user_tecmanager)._compute_personal_stage_id()
        self.assertEqual(self.task_1.with_user(self.user_tecmanager).personal_stage_type_id, task_1_manager_stage,
            'Modifying the personal stage of Tec User should not have affected the personal stage of Tec Manager.')

        self.task_2.with_user(self.user_tecmanager).personal_stage_type_id = self.manager_stages[1]
        self.assertEqual(self.task_1.with_user(self.user_tecmanager).personal_stage_type_id, task_1_manager_stage,
            'Modifying the personal stage on task 2 for Tec Manager should not have affected the stage on task 1.')

    def test_personal_stage_search(self):
        self.task_2.user_ids += self.user_tecuser
        # Make sure both personal stages are different
        self.task_1.with_user(self.user_tecuser).personal_stage_type_id = self.user_stages[0]
        self.task_2.with_user(self.user_tecuser).personal_stage_type_id = self.user_stages[1]
        tasks = self.env['tec.task'].with_user(self.user_tecuser).search([('personal_stage_type_id', '=', self.user_stages[0].id)])
        self.assertTrue(tasks, 'The search result should not be empty.')
        for task in tasks:
            self.assertEqual(task.personal_stage_type_id, self.user_stages[0],
                'The search should only have returned task that are in the inbox personal stage.')

    def test_personal_stage_read_group(self):
        self.task_1.user_ids += self.user_tecmanager
        self.task_1.with_user(self.user_tecmanager).personal_stage_type_id = self.manager_stages[1]
        #Makes sure the personal stage for tec manager is saved in the database
        self.env.flush_all()
        read_group_user = self.env['tec.task'].with_user(self.user_tecuser).read_group(
            [('user_ids', '=', self.user_tecuser.id)], fields=['sequence:avg'], groupby=['personal_stage_type_ids'])
        # Check that the result is at least a bit coherent
        self.assertEqual(len(self.user_stages), len(read_group_user),
            'read_group should return %d groups' % len(self.user_stages))
        # User has only one task assigned the sum of all counts should be 1
        total = 0
        for group in read_group_user:
            total += group['personal_stage_type_ids_count']
        self.assertEqual(1, total,
            'read_group should not have returned more tasks than the user is assigned to.')
        read_group_manager = self.env['tec.task'].with_user(self.user_tecmanager).read_group(
            [('user_ids', '=', self.user_tecmanager.id)], fields=['sequence:avg'], groupby=['personal_stage_type_ids'])
        self.assertEqual(len(self.manager_stages), len(read_group_manager),
            'read_group should return %d groups' % len(self.user_stages))
        total = 0
        total_stage_0 = 0
        total_stage_1 = 0
        for group in read_group_manager:
            total += group['personal_stage_type_ids_count']
            # Check that we have a task in both stages
            if group['personal_stage_type_ids'][0] == self.manager_stages[0].id:
                total_stage_0 += 1
            elif group['personal_stage_type_ids'][0] == self.manager_stages[1].id:
                total_stage_1 += 1
        self.assertEqual(2, total,
            'read_group should not have returned more tasks than the user is assigned to.')
        self.assertEqual(1, total_stage_0)
        self.assertEqual(1, total_stage_1)

@tagged('-at_install', 'post_install')
class TestPersonalStageTour(HttpCase, TestTecCommon):

    def test_personal_stage_tour(self):
        # Test customizing personal stages as a tec user
        self.start_tour('/web', 'personal_stage_tour', login="armandel")
