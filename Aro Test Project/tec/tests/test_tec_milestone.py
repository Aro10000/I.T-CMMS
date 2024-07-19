# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import Form, tagged

from .test_tec_base import TestTecCommon


@tagged('-at_install', 'post_install')
class TestTecMilestone(TestTecCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.milestone = cls.env['tec.milestone'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test Milestone',
            'tec_id': cls.tec_pigs.id,
        })

    def test_milestones_settings_change(self):
        # To be sure the feature is disabled globally to begin the test.
        self.env['res.config.settings'] \
            .create({'group_tec_milestone': False}) \
            .execute()
        self.assertFalse(self.env.user.has_group('tec.group_tec_milestone'), 'The "Milestones" feature should not be globally enabled by default.')
        self.assertFalse(self.tec_pigs.allow_milestones, 'The "Milestones" feature should not be enabled by default.')
        self.env['res.config.settings'] \
            .create({'group_tec_milestone': True}) \
            .execute()
        self.assertTrue(self.env.user.has_group('tec.group_tec_milestone'), 'The "Milestones" feature should globally be enabled.')
        self.assertTrue(self.tec_pigs.allow_milestones, 'The "Milestones" feature should be enabled by default on the tec when the feature is enabled.')
        tec = self.env['tec.tec'].create({'name': 'Test allow_milestones on New Tec'})
        self.assertTrue(tec.allow_milestones, 'The "Milestones" feature should be enabled by default when the feature is enabled globally.')

        with Form(self.env['tec.tec']) as tec_form:
            tec_form.name = 'My Mouses Tec'
            self.assertTrue(tec_form.allow_milestones, 'New tecs allow_milestones should be True by default.')

    def test_change_tec_in_task(self):
        """ Test when a task is linked to a milestone and when we change its tec the milestone is removed

            Test Case:
            =========
            1) Set a milestone on the task
            2) Change the tec of that task
            3) Check no milestone is linked to the task
        """
        self.task_1.milestone_id = self.milestone
        self.assertEqual(self.task_1.milestone_id, self.milestone)

        self.task_1.tec_id = self.tec_goats
        self.assertFalse(self.task_1.milestone_id, 'No milestone should be linked to the task since its tec has changed')

    def test_duplicate_tec_duplicates_milestones_on_tasks(self):
        """
        Test when we duplicate the tec with tasks linked to its' milestones,
        that the tasks in the new tec are also linked to the duplicated milestones of the new tec
        We can't really robustly test that the mapping of task -> milestone is the same in the old and new tec,
        the workaround way of testing the mapping is basing ourselves on unique names and check that those are equals in the test.
        """
        # original unique_names, used to map between the original -> copy
        unique_name_1 = "unique_name_1"
        unique_name_2 = "unique_name_2"
        unique_names = [unique_name_1, unique_name_2]
        tec = self.env['tec.tec'].create({
            'name': 'Test tec',
            'allow_milestones': True,
        })
        milestones = self.env['tec.milestone'].create([{
            'name': unique_name_1,
            'tec_id': tec.id,
        }, {
            'name': unique_name_2,
            'tec_id': tec.id,
        }])
        tasks = self.env['tec.task'].create([{
            'name': unique_name_1,
            'tec_id': tec.id,
            'milestone_id': milestones[0].id,
        }, {
            'name': unique_name_2,
            'tec_id': tec.id,
            'milestone_id': milestones[1].id,
        }])
        self.assertEqual(tasks[0].milestone_id, milestones[0])
        self.assertEqual(tasks[1].milestone_id, milestones[1])
        tec_copy = tec.copy()
        self.assertNotEqual(tec_copy.milestone_ids, False)
        self.assertEqual(tec.milestone_ids.mapped('name'), tec_copy.milestone_ids.mapped('name'))
        self.assertNotEqual(tec_copy.task_ids, False)
        for milestone in tec_copy.task_ids.milestone_id:
            self.assertTrue(milestone in tec_copy.milestone_ids)
        for unique_name in unique_names:
            orig_task = tec.task_ids.filtered(lambda t: t.name == unique_name)
            copied_task = tec_copy.task_ids.filtered(lambda t: t.name == unique_name)
            self.assertEqual(orig_task.name, copied_task.name, "The copied_task should be a copy of the original task")
            self.assertNotEqual(copied_task.milestone_id, False,
                                "We should copy the milestone and it shouldn't be reset to false from _compute_milestone_id")
            self.assertEqual(orig_task.milestone_id.name, copied_task.milestone_id.name,
                             "the copied milestone should be a copy if the original ")
