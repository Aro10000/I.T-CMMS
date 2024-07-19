# -*- coding: utf-8 -*-

from odoo import Command
from odoo.addons.tec.tests.test_tec_base import TestTecCommon
from odoo.tests import tagged
from odoo.tests.common import Form

@tagged('-at_install', 'post_install')
class TestTecSubtasks(TestTecCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Enable the company setting
        cls.env['res.config.settings'].create({
            'group_subtask_tec': True
        }).execute()

    def test_task_display_tec_with_default_form(self):
        """
            Create a task in the default task form should take the tec set in the form or the default tec in the context
        """
        with Form(self.env['tec.task'].with_context({'tracking_disable': True})) as task_form:
            task_form.name = 'Test Task 1'
            task_form.tec_id = self.tec_pigs
        task = task_form.save()

        self.assertEqual(task.tec_id, self.tec_pigs, "The tec should be assigned.")
        self.assertEqual(task.display_tec_id, task.tec_id, "The display tec of a first layer task should be assigned to tec_id.")

        with Form(self.env['tec.task'].with_context({'tracking_disable': True, 'default_tec_id': self.tec_pigs.id})) as task_form:
            task_form.name = 'Test Task 2'
        task = task_form.save()

        self.assertEqual(task.tec_id, self.tec_pigs, "The tec should be assigned from the default tec.")
        self.assertEqual(task.display_tec_id, task.tec_id, "The display tec of a first layer task should be assigned to tec_id.")

    def test_task_display_tec_with_task_form2(self):
        """
            Create a task in the task form 2 should take the tec set in the form or the default tec in the context
        """
        with Form(self.env['tec.task'].with_context({'tracking_disable': True}), view="tec.view_task_form2") as task_form:
            task_form.name = 'Test Task 1'
            task_form.tec_id = self.tec_pigs
        task = task_form.save()

        self.assertEqual(task.tec_id, self.tec_pigs, "The tec should be assigned.")
        self.assertEqual(task.display_tec_id, task.tec_id, "The display tec of a first layer task should be assigned to tec_id.")

        with Form(self.env['tec.task'].with_context({'tracking_disable': True, 'default_tec_id': self.tec_pigs.id}), view="tec.view_task_form2") as task_form:
            task_form.name = 'Test Task 2'
        task = task_form.save()

        self.assertEqual(task.tec_id, self.tec_pigs, "The tec should be assigned from the default tec.")
        self.assertEqual(task.display_tec_id, task.tec_id, "The display tec of a first layer task should be assigned to tec_id.")

    def test_task_display_tec_with_quick_create_task_form(self):
        """
            Create a task in the quick create form should take the default tec in the context
        """
        with Form(self.env['tec.task'].with_context({'tracking_disable': True, 'default_tec_id': self.tec_pigs.id}), view="tec.quick_create_task_form") as task_form:
            task_form.name = 'Test Task 2'
        task = task_form.save()

        self.assertEqual(task.tec_id, self.tec_pigs, "The tec should be assigned from the default tec.")
        self.assertEqual(task.display_tec_id, task.tec_id, "The display tec of a first layer task should be assigned to tec_id.")

    def test_task_display_tec_with_any_task_form(self):
        """
            Create a task in any form should take the default tec in the context
        """
        form_views = self.env['ir.ui.view'].search([('model', '=', 'tec.task'), ('type', '=', 'form')])
        for form_view in form_views:
            task_form = Form(self.env['tec.task'].with_context({'tracking_disable': True, 'default_tec_id': self.tec_pigs.id, 'default_name': 'Test Task 1'}), view=form_view)
            # Some views have the `name` field invisible
            # As the goal is simply to test the default tec field and not the name, we can skip setting the name
            # in the view and set it using `default_name` instead
            task = task_form.save()

            self.assertEqual(task.tec_id, self.tec_pigs, "The tec should be assigned from the default tec, form_view name : %s." % form_view.name)
            self.assertEqual(task.display_tec_id, task.tec_id, "The display tec of a first layer task should be assigned to tec_id, form_view name : %s." % form_view.name)

    def test_subtask_display_tec(self):
        """
            1) Create a subtask
                - Should have the same tec as its parent
                - Shouldn't have a display tec set.
            2) Set display tec on subtask
                - Should not change parent tec
                - Should change the subtask tec
                - Display tec should be correct
            3) Reset the display tec to False
                - Should make the tec equal to parent tec
                - Display tec should be correct
            4) Change parent task tec
                - Should make the subtask tec follow parent tec
                - Display tec should stay false
            5) Set display tec on subtask and change parent task tec
                - Should make the subtask tec follow new display tec id
                - Display tec should be correct
            6) Remove parent task:
                - The tec id should remain unchanged
                - The display tec id should follow the tec id
            7) Remove display tec id then parent id:
                - The tec id should be the one from the parent :
                    - Since the display tec id was removed, the tec id is updated to the parent one
                - The display tec id should follow the tec id
        """
        # 1)
        test_subtask_1 = self.env['tec.task'].create({
            'name': 'Test Subtask 1',
        })
        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.child_ids.add(test_subtask_1)

        self.assertEqual(self.task_1.child_ids.tec_id, self.tec_pigs, "The tec should be assigned from the default tec.")
        self.assertFalse(self.task_1.child_ids.display_tec_id, "The display tec of a sub task should be false to tec_id.")

        # 2)
        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.child_ids[0].display_tec_id = self.tec_goats
        self.assertEqual(self.task_1.tec_id, self.tec_pigs, "Changing the tec of a subtask should not change parent tec")
        self.assertEqual(self.task_1.child_ids.display_tec_id, self.tec_goats, "Display Tec of the task should be well assigned")
        self.assertEqual(self.task_1.child_ids.tec_id, self.tec_goats, "Changing display tec id on a subtask should change tec id")

        # 3)
        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.child_ids[0].display_tec_id = self.env['tec.tec']

        self.assertFalse(self.task_1.child_ids.display_tec_id, "Display Tec of the task should be well assigned, to False")
        self.assertEqual(self.task_1.child_ids.tec_id, self.tec_pigs, "Resetting display tec to False on a subtask should change tec id to parent tec id")

        # 4)
        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.tec_id = self.tec_goats

        self.assertEqual(self.task_1.tec_id, self.tec_goats, "Parent tec should change.")
        self.assertFalse(self.task_1.child_ids.display_tec_id, "Display Tec of the task should be False")
        self.assertEqual(self.task_1.child_ids.tec_id, self.tec_goats, "Resetting display tec to False on a subtask should follow tec of its parent")

        # 5)
        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.child_ids[0].display_tec_id = self.tec_goats
            task_form.tec_id = self.tec_pigs

        self.assertEqual(self.task_1.tec_id, self.tec_pigs, "Parent tec should change back.")
        self.assertEqual(self.task_1.child_ids.display_tec_id, self.tec_goats, "Display Tec of the task should be well assigned")
        self.assertEqual(self.task_1.child_ids.tec_id, self.tec_goats, "Changing display tec id on a subtask should change tec id")

        # Debug mode required for `parent_id` to be visible in the view
        with self.debug_mode():
            # 6)
            with Form(self.task_1.child_ids.with_context({'tracking_disable': True})) as subtask_form:
                subtask_form.parent_id = self.env['tec.task']
            orphan_subtask = subtask_form.save()

            self.assertEqual(orphan_subtask.display_tec_id, self.tec_goats, "Display Tec of the task should be well assigned")
            self.assertEqual(orphan_subtask.tec_id, self.tec_goats, "Changing display tec id on a subtask should change tec id")
            self.assertFalse(orphan_subtask.parent_id, "Parent should be false")

            # 7)
            test_subtask_1 = self.env['tec.task'].create({
                'name': 'Test Subtask 1',
            })
            with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
                task_form.child_ids.add(test_subtask_1)
                task_form.child_ids[0].display_tec_id = self.tec_goats
            with Form(self.task_1.child_ids.with_context({'tracking_disable': True})) as subtask_form:
                subtask_form.display_tec_id = self.env['tec.tec']
                subtask_form.parent_id = self.env['tec.task']
            orphan_subtask = subtask_form.save()

            self.assertEqual(orphan_subtask.tec_id, self.tec_pigs, "Removing parent should not change tec")
            self.assertEqual(orphan_subtask.display_tec_id, self.tec_pigs, "Removing parent should make the display tec set as tec.")

    def test_subtask_stage(self):
        """
            The stage of the new child must be the default one of the tec
        """
        stage_a = self.env['tec.task.type'].create({'name': 'a', 'sequence': 1})
        stage_b = self.env['tec.task.type'].create({'name': 'b', 'sequence': 10})
        self.tec_pigs.type_ids |= stage_a
        self.tec_pigs.type_ids |= stage_b

        test_subtask_1 = self.env['tec.task'].create({
            'name': 'Test Subtask 1',
        })
        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.child_ids.add(test_subtask_1)

        self.assertEqual(self.task_1.child_ids.stage_id, stage_a, "The stage of the child task should be the default one of the tec.")

        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.stage_id = stage_b

        self.assertEqual(self.task_1.child_ids.stage_id, stage_a, "The stage of the child task should remain the same while changing parent task stage.")

        test_subtask_2 = self.env['tec.task'].create({
            'name': 'Test Subtask 2',
        })
        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.child_ids.remove(test_subtask_1.id)
            task_form.child_ids.add(test_subtask_2)

        self.assertEqual(self.task_1.child_ids.stage_id, stage_a, "The stage of the child task should be the default one of the tec even if parent stage id is different.")

        with Form(self.task_1.with_context({'tracking_disable': True})) as task_form:
            task_form.child_ids[0].display_tec_id = self.tec_goats

        self.assertEqual(self.task_1.child_ids.stage_id.name, "New", "The stage of the child task should be the default one of the display tec id, once set.")

    def test_copy_tec_with_subtasks(self):
        self.tec_goats.allow_subtasks = True
        self.env['tec.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Parent Task',
            'tec_id': self.tec_goats.id,
            'child_ids': [
                Command.create({'name': 'child 1', 'stage_id': self.tec_goats.type_ids[0].id}),
                Command.create({'name': 'child 2', 'display_tec_id': self.tec_goats.id}),
                Command.create({'name': 'child 3', 'display_tec_id': self.tec_pigs.id}),
                Command.create({'name': 'child 4 with subtask', 'child_ids': [Command.create({'name': 'child 5'}), Command.create({'name': 'child 6 with tec', 'display_tec_id': self.tec_goats.id})]}),
                Command.create({'name': 'child archived', 'active': False}),
            ],
            'stage_id': self.tec_goats.type_ids[0].id
        })
        task_count_with_subtasks_including_archived_in_tec_goats = self.tec_goats.with_context(active_test=False).task_count_with_subtasks
        task_count_in_tec_pigs = self.tec_pigs.task_count
        self.tec_goats._compute_task_count()  # recompute without archived tasks and subtasks
        task_count_in_tec_goats = self.tec_goats.task_count
        tec_goats_duplicated = self.tec_goats.copy()
        self.tec_pigs._compute_task_count()  # retrigger since a new task should be added in the tec after the duplication of Tec Goats
        self.assertEqual(
            tec_goats_duplicated.with_context(active_test=False).task_count_with_subtasks,
            task_count_with_subtasks_including_archived_in_tec_goats - 1,
            'The number of duplicated tasks (subtasks included) should be equal to the number of all tasks (with active subtasks included) of both tecs, '
            'that is only the active subtasks are duplicated.')
        self.assertEqual(self.tec_goats.task_count, task_count_in_tec_goats, 'The number of tasks should be the same before and after the duplication of this tec.')
        self.assertEqual(self.tec_pigs.task_count, task_count_in_tec_pigs + 1, 'The tec pigs should an additional task after the duplication of the tec goats.')
        self.assertEqual(tec_goats_duplicated.tasks[0].child_ids[0].stage_id.id, self.tec_goats.type_ids[0].id, 'The stage of subtasks should be copied too.')

    def test_subtask_creation_with_form(self):
        """
            1) test the creation of sub-tasks through the notebook
            2) set a parent task on an existing task
            3) test the creation of sub-sub-tasks
            4) check the correct nb of sub-tasks is displayed in the 'sub-tasks' stat button and on the parent task kanban card
            5) sub-tasks should be copied when the parent task is duplicated
        """
        test_subtask_1 = self.env['tec.task'].create({
            'name': 'Test Subtask 1',
        })

        task_form = Form(self.task_1.with_context({'tracking_disable': True}))
        task_form.child_ids.add(test_subtask_1)
        task_form.child_ids[0].display_tec_id = self.env['tec.tec']
        task = task_form.save()

        child_subtask = self.task_1.child_ids[0]
        test_subtask_2 = self.env['tec.task'].create({
            'name': 'Test Subtask 2',
        })

        with Form(child_subtask.with_context(tracking_disable=True)) as subtask_form:
            subtask_form.child_ids.add(test_subtask_2)
            subtask_form.child_ids[0].display_tec_id = self.env['tec.tec']

        self.assertEqual(task.subtask_count, 2, "Parent task should have 2 children")
        task_2 = task.copy()
        self.assertEqual(task_2.subtask_count, 2, "If the parent task is duplicated then the sub task should be copied")
