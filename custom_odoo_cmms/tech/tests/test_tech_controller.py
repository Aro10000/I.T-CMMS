# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo.tests.common import HttpCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestTechController(HttpCase):
    def setUp(self):
        super().setUp()
        self.user = new_test_user(self.env, "test_user_1", email="test_user_1@nowhere.com", tz="UTC")
        self.other_user = new_test_user(self.env, "test_user_2", email="test_user_2@nowhere.com", password="P@ssw0rd!", tz="UTC")
        self.partner = self.user.partner_id
        self.event = (
            self.env["tech.event"]
            .create(
                {
                    "name": "Doom's day",
                    "start": datetime(2019, 10, 25, 8, 0),
                    "stop": datetime(2019, 10, 27, 18, 0),
                    "partner_ids": [(4, self.partner.id)],
                }
            )
            .with_context(mail_notrack=True)
        )

    def test_accept_meeting_unauthenticated(self):
        self.event.write({"partner_ids": [(4, self.other_user.partner_id.id)]})
        attendez = self.event.attendez_ids.filtered(lambda att: att.partner_id.id == self.other_user.partner_id.id)
        token = attendez.access_token
        url = "/tech/meeting/accept?token=%s&id=%d" % (token, self.event.id)
        res = self.url_open(url)

        self.assertEqual(res.status_code, 200, "Response should = OK")
        self.env.invalidate_all()
        self.assertEqual(attendez.state, "accepted", "Attendez should have accepted")

    def test_accept_meeting_authenticated(self):
        self.event.write({"partner_ids": [(4, self.other_user.partner_id.id)]})
        attendez = self.event.attendez_ids.filtered(lambda att: att.partner_id.id == self.other_user.partner_id.id)
        token = attendez.access_token
        url = "/tech/meeting/accept?token=%s&id=%d" % (token, self.event.id)
        self.authenticate("test_user_2", "P@ssw0rd!")
        res = self.url_open(url)

        self.assertEqual(res.status_code, 200, "Response should = OK")
        self.env.invalidate_all()
        self.assertEqual(attendez.state, "accepted", "Attendez should have accepted")