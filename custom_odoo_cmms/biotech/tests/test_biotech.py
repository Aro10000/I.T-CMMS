# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo.tests.common import TransactionCase
from dateutil import relativedelta
import datetime

class TestEquipment(TransactionCase):
    """ Test used to check that when doing equipment/biotech_request/equipment_category creation."""

    def setUp(self):
        super(TestEquipment, self).setUp()
        self.equipment = self.env['biotech.equipment']
        self.biotech_request = self.env['biotech.request']
        self.res_users = self.env['res.users']
        self.biotech_team = self.env['biotech.team']
        self.main_company = self.env.ref('base.main_company')
        res_user = self.env.ref('base.group_user')
        res_manager = self.env.ref('biotech.group_equipment_manager')

        self.user = self.res_users.create(dict(
            name="Normal User/Employee",
            company_id=self.main_company.id,
            login="emp",
            email="empuser@yourcompany.example.com",
            groups_id=[(6, 0, [res_user.id])]
        ))

        self.manager = self.res_users.create(dict(
            name="Equipment Manager",
            company_id=self.main_company.id,
            login="hm",
            email="eqmanager@yourcompany.example.com",
            groups_id=[(6, 0, [res_manager.id])]
        ))

        self.equipment_monitor = self.env['biotech.equipment.category'].create({
            'name': 'Monitors - Test',
        })

    def test_10_equipment_request_category(self):

        # Create a new equipment
        equipment_01 = self.equipment.with_user(self.manager).create({
            'name': 'Samsung Monitor "15',
            'category_id': self.equipment_monitor.id,
            'technician_user_id': self.ref('base.user_root'),
            'owner_user_id': self.user.id,
            'assign_date': time.strftime('%Y-%m-%d'),
            'serial_no': 'MT/127/18291015',
            'model': 'NP355E5X',
            'color': 3,
        })

        # Check that equipment is created or not
        assert equipment_01, "Equipment not created"

        # Create new biotech request
        biotech_request_01 = self.biotech_request.with_user(self.user).create({
            'name': 'Resolution is bad',
            'user_id': self.user.id,
            'owner_user_id': self.user.id,
            'equipment_id': equipment_01.id,
            'color': 7,
            'stage_id': self.ref('biotech.stage_0'),
            'biotech_team_id': self.ref('biotech.equipment_team_biotech')
        })

        # I check that biotech_request is created or not
        assert biotech_request_01, "Biotech Request not created"

        # I check that Initially biotech request is in the "New Request" stage
        self.assertEqual(biotech_request_01.stage_id.id, self.ref('biotech.stage_0'))

        # I check that change the biotech_request stage on click statusbar
        biotech_request_01.with_user(self.user).write({'stage_id': self.ref('biotech.stage_1')})

        # I check that biotech request is in the "In Progress" stage
        self.assertEqual(biotech_request_01.stage_id.id, self.ref('biotech.stage_1'))

    def test_20_cron(self):
        """ Check the cron creates the necessary preventive biotech requests"""
        equipment_cron = self.equipment.create({
            'name': 'High Biotech Monitor because of Color Calibration',
            'category_id': self.equipment_monitor.id,
            'technician_user_id': self.ref('base.user_root'),
            'owner_user_id': self.user.id,
            'assign_date': time.strftime('%Y-%m-%d'),
            'period': 7,
            'color': 3,
        })

        biotech_request_cron = self.biotech_request.create({
            'name': 'Need a special calibration',
            'user_id': self.user.id,
            'request_date': (datetime.datetime.now() + relativedelta.relativedelta(days=7)).strftime('%Y-%m-%d'),
            'biotech_type': 'preventive',
            'owner_user_id': self.user.id,
            'equipment_id': equipment_cron.id,
            'color': 7,
            'stage_id': self.ref('biotech.stage_0'),
            'biotech_team_id': self.ref('biotech.equipment_team_biotech')
        })

        self.env['biotech.equipment']._cron_generate_requests()
        # As it is generating the requests for one month in advance, we should have 4 requests in total
        tot_requests = self.biotech_request.search([('equipment_id', '=', equipment_cron.id)])
        self.assertEqual(len(tot_requests), 1, 'The cron should have generated just 1 request for the High Biotech Monitor.')

    def test_21_cron(self):
        """ Check the creation of biotech requests by the cron"""

        team_test = self.biotech_team.create({
            'name': 'team_test',
        })
        equipment = self.equipment.create({
            'name': 'High Biotech Monitor because of Color Calibration',
            'category_id': self.equipment_monitor.id,
            'technician_user_id': self.ref('base.user_root'),
            'owner_user_id': self.user.id,
            'assign_date': time.strftime('%Y-%m-%d'),
            'period': 7,
            'color': 3,
            'biotech_team_id': team_test.id,
            'biotech_duration': 3.0,
        })

        self.env['biotech.equipment']._cron_generate_requests()
        tot_requests = self.biotech_request.search([('equipment_id', '=', equipment.id)])
        self.assertEqual(len(tot_requests), 1, 'The cron should have generated just 1 request for the High Biotech Monitor.')
        self.assertEqual(tot_requests.biotech_team_id.id, team_test.id, 'The biotech team should be the same as equipment one')
        self.assertEqual(tot_requests.duration, 3.0, 'Equipement biotech duration is not the same as the request one')
