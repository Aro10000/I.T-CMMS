# -*- coding: utf-8 -*-

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestTecSharingUi(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = cls.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nolog': True}).create({
            'name': 'Georges',
            'login': 'georges1',
            'password': 'georges1',
            'email': 'georges@tec.portal',
            'signature': 'SignGeorges',
            'notification_type': 'email',
            'groups_id': [Command.set([cls.env.ref('base.group_portal').id])],
        })

        cls.partner_portal = cls.env['res.partner'].with_context({'mail_create_nolog': True}).create({
            'name': 'Georges',
            'email': 'georges@tec.portal',
            'company_id': False,
            'user_ids': [user.id],
        })
        cls.tec_portal = cls.env['tec.tec'].with_context({'mail_create_nolog': True}).create({
            'name': 'Tec Sharing',
            'privacy_visibility': 'portal',
            'alias_name': 'tec+sharing',
            'partner_id': cls.partner_portal.id,
            'type_ids': [
                Command.create({'name': 'To Do', 'sequence': 1}),
                Command.create({'name': 'Done', 'sequence': 10})
            ],
        })

    def test_01_tec_sharing(self):
        """ Test Tec Sharing UI with an internal user """
        self.start_tour("/web", 'tec_sharing_tour', login="admin")

    def test_02_tec_sharing(self):
        """ Test tec sharing ui with a portal user.

            The additional data created here are the data created in the first test with the tour js.

            Since a problem to logout Mitchell Admin to log in as Georges user, this test is created
            to launch a tour with portal user.
        """
        tec_share_wizard = self.env['tec.share.wizard'].create({
            'access_mode': 'edit',
            'res_model': 'tec.tec',
            'res_id': self.tec_portal.id,
            'partner_ids': [
                Command.link(self.partner_portal.id),
            ],
        })
        tec_share_wizard.action_send_mail()

        self.tec_portal.write({
            'task_ids': [Command.create({
                'name': "Test Tec Sharing",
                'stage_id': self.tec_portal.type_ids.filtered(lambda stage: stage.sequence == 10)[:1].id,
            })],
        })
        self.start_tour("/my/tecs", 'portal_tec_sharing_tour', login='georges1')
