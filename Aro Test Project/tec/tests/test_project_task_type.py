# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo.addons.tec.tests.test_tec_base import TestTecCommon


class TestTecTaskType(TestTecCommon):

    @classmethod
    def setUpClass(cls):
        super(TestTecTaskType, cls).setUpClass()

        cls.stage_created = cls.env['tec.task.type'].create({
            'name': 'Stage Already Created',
        })

    def test_create_stage(self):
        '''
        Verify that it is not possible to add to a newly created stage a `user_id` and a `tec_ids`
        '''
        with self.assertRaises(UserError):
            self.env['tec.task.type'].create({
                'name': 'New Stage',
                'user_id': self.uid,
                'tec_ids': [self.tec_goats.id],
            })

    def test_modify_existing_stage(self):
        '''
        - case 1: [`user_id`: not set, `tec_ids`: not set] | Add `user_id` and `tec_ids` => UserError
        - case 2: [`user_id`: set, `tec_ids`: not set]  | Add `tec_ids` => UserError
        - case 3: [`user_id`: not set, `tec_ids`: set] | Add `user_id` => UserError
        '''
        # case 1
        with self.assertRaises(UserError):
            self.stage_created.write({
                'user_id': self.uid,
                'tec_ids': [self.tec_goats.id],
            })

        # case 2
        self.stage_created.write({
            'user_id': self.uid,
        })
        with self.assertRaises(UserError):
            self.stage_created.write({
                'tec_ids': [self.tec_goats.id],
            })

        # case 3
        self.stage_created.write({
            'user_id': False,
            'tec_ids': [self.tec_goats.id],
        })
        with self.assertRaises(UserError):
            self.stage_created.write({
                'user_id': self.uid,
            })
