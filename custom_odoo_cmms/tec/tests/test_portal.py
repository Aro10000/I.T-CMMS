# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.tec.tests.test_access_rights import TestTecPortalCommon
from odoo.exceptions import AccessError
from odoo.tools import mute_logger


class TestPortalTec(TestTecPortalCommon):
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_portal_tec_access_rights(self):
        pigs = self.tec_pigs
        pigs.write({'privacy_visibility': 'portal'})

        # Do: Alfred reads tec -> ok (employee ok public)
        pigs.with_user(self.user_tecuser).read(['user_id'])
        # Test: all tec tasks visible
        tasks = self.env['tec.task'].with_user(self.user_tecuser).search([('tec_id', '=', pigs.id)])
        self.assertEqual(tasks, self.task_1 | self.task_2 | self.task_3 | self.task_4 | self.task_5 | self.task_6,
                         'access rights: tec user should see all tasks of a portal tec')

        # Do: Bert reads tec -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])
        # Test: no tec task searchable
        self.assertRaises(AccessError, self.env['tec.task'].with_user(self.user_noone).search, [('tec_id', '=', pigs.id)])

        # Data: task follower
        pigs.with_user(self.user_tecmanager).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_1.with_user(self.user_tecuser).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_3.with_user(self.user_tecuser).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        # Do: Chell reads tec -> ok (portal ok public)
        pigs.with_user(self.user_portal).read(['user_id'])
        # Do: Donovan reads tec -> ko (public ko portal)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Test: no access right to tec.task
        self.assertRaises(AccessError, self.env['tec.task'].with_user(self.user_public).search, [])
        # Data: task follower cleaning
        self.task_1.with_user(self.user_tecuser).message_unsubscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_3.with_user(self.user_tecuser).message_unsubscribe(partner_ids=[self.user_portal.partner_id.id])
