# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase, new_test_user, Form
from odoo import fields, Command


class TestEventNotifications(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(cls.env, 'xav', email='em@il.com', notification_type='inbox')
        cls.event = cls.env['tech.event'].with_user(cls.user).create({
            'name': "Doom's day",
            'start': datetime(2019, 10, 25, 8, 0),
            'stop': datetime(2019, 10, 27, 18, 0),
        }).with_context(mail_notrack=True)
        cls.partner = cls.user.partner_id

    def test_attendez_added(self):
        self.event.partner_ids = self.partner
        self.assertTrue(self.event.attendez_ids, "It should have created an attendez")
        self.assertEqual(self.event.attendez_ids.partner_id, self.partner, "It should be linked to the partner")
        self.assertIn(self.partner, self.event.message_follower_ids.partner_id, "He should be follower of the event")

    def test_attendez_added_create(self):
        event = self.env['tech.event'].create({
            'name': "Doom's day",
            'start': datetime(2019, 10, 25, 8, 0),
            'stop': datetime(2019, 10, 27, 18, 0),
            'partner_ids': [(4, self.partner.id)],
        })
        self.assertTrue(event.attendez_ids, "It should have created an attendez")
        self.assertEqual(event.attendez_ids.partner_id, self.partner, "It should be linked to the partner")
        self.assertIn(self.partner, event.message_follower_ids.partner_id, "He should be follower of the event")

    def test_attendez_added_create_with_specific_states(self):
        """
        When an event is created from an external tech account (such as Google) which is not linked to an
        Odoo account, attendez info such as email and state are given at sync.
        In this case, attendez_ids should be created accordingly.
        """
        organizer_partner = self.env['res.partner'].create({'name': "orga", "email": "orga@google.com"})
        event = self.env['tech.event'].with_user(self.user).create({
            'name': "Doom's day",
            'start': datetime(2019, 10, 25, 8, 0),
            'stop': datetime(2019, 10, 27, 18, 0),
            'attendez_ids': [
                (0, 0, {'partner_id': self.partner.id, 'state': 'needsAction'}),
                (0, 0, {'partner_id': organizer_partner.id, 'state': 'accepted'})
            ],
            'partner_ids': [(4, self.partner.id), (4, organizer_partner.id)],
        })
        attendezs_info = [(a.email, a.state) for a in event.attendez_ids]
        self.assertEqual(len(event.attendez_ids), 2)
        self.assertIn((self.partner.email, "needsAction"), attendezs_info)
        self.assertIn((organizer_partner.email, "accepted"), attendezs_info)

    def test_attendez_added_multi(self):
        event = self.env['tech.event'].create({
            'name': "Doom's day",
            'start': datetime(2019, 10, 25, 8, 0),
            'stop': datetime(2019, 10, 27, 18, 0),
        })
        events = self.event | event
        events.partner_ids = self.partner
        self.assertEqual(len(events.attendez_ids), 2, "It should have created one attendez per event")

    def test_attendez_added_write(self):
        """Test that writing ids directly on partner_ids instead of commands is handled."""
        self.event.write({'partner_ids': [self.partner.id]})
        self.assertEqual(self.event.attendez_ids.partner_id, self.partner, "It should be linked to the partner")

    def test_existing_attendez_added(self):
        self.event.partner_ids = self.partner
        attendez = self.event.attendez_ids
        self.event.write({'partner_ids': [(4, self.partner.id)]})  # Add existing partner
        self.assertEqual(self.event.attendez_ids, attendez, "It should not have created an new attendez record")

    def test_attendez_add_self(self):
        self.event.with_user(self.user).partner_ids = self.partner
        self.assertTrue(self.event.attendez_ids, "It should have created an attendez")
        self.assertEqual(self.event.attendez_ids.partner_id, self.partner, "It should be linked to the partner")
        self.assertEqual(self.event.attendez_ids.state, 'accepted', "It should be accepted for the current user")

    def test_attendez_removed(self):
        partner_bis = self.env['res.partner'].create({'name': "Xavier"})
        self.event.partner_ids = partner_bis
        attendez = self.event.attendez_ids
        self.event.partner_ids |= self.partner
        self.event.partner_ids -= self.partner
        self.assertEqual(attendez, self.event.attendez_ids, "It should not have re-created an attendez record")
        self.assertNotIn(self.partner, self.event.attendez_ids.partner_id, "It should have removed the attendez")
        self.assertNotIn(self.partner, self.event.message_follower_ids.partner_id, "It should have unsubscribed the partner")
        self.assertIn(partner_bis, self.event.attendez_ids.partner_id, "It should have left the attendez")

    def test_attendez_without_email(self):
        self.partner.email = False
        self.event.partner_ids = self.partner

        self.assertTrue(self.event.attendez_ids)
        self.assertEqual(self.event.attendez_ids.partner_id, self.partner)
        self.assertTrue(self.event.invalid_email_partner_ids)
        self.assertEqual(self.event.invalid_email_partner_ids, self.partner)

    def test_attendez_with_invalid_email(self):
        self.partner.email = "I'm an invalid email"
        self.event.partner_ids = self.partner

        self.assertTrue(self.event.attendez_ids)
        self.assertEqual(self.event.attendez_ids.partner_id, self.partner)
        self.assertTrue(self.event.invalid_email_partner_ids)
        self.assertEqual(self.event.invalid_email_partner_ids, self.partner)

    def test_default_attendez(self):
        """
        Check if priority list id correctly followed
        1) vals_list[0]['attendez_ids']
        2) vals_list[0]['partner_ids']
        3) context.get('default_attendez_ids')
        """
        partner_bis = self.env['res.partner'].create({'name': "Xavier"})
        event = self.env['tech.event'].with_user(
            self.user
        ).with_context(
            default_attendez_ids=[(0, 0, {'partner_id': partner_bis.id})]
        ).create({
            'name': "Doom's day",
            'partner_ids': [(4, self.partner.id)],
            'start': datetime(2019, 10, 25, 8, 0),
            'stop': datetime(2019, 10, 27, 18, 0),
        })
        self.assertIn(self.partner, event.attendez_ids.partner_id, "Partner should be in attendez")
        self.assertNotIn(partner_bis, event.attendez_ids.partner_id, "Partner bis should not be in attendez")

    def test_push_meeting_start(self):
        """
        Checks that you can push the start date of an all day meeting.
        """
        attendez = self.env['res.partner'].create({
            'name': "Xavier",
            'email': "xavier@example.com",
            })
        event = self.env['tech.event'].create({
            'name': "Doom's day",
            'attendez_ids': [Command.create({'partner_id': attendez.id})],
            'allday': True,
            'start_date': fields.Date.today(),
            'stop_date': fields.Date.today(),
        })
        initial_start = event.start
        with Form(event) as event_form:
            event_form.stop_date = datetime.today() + relativedelta(days=1)
            event_form.start_date = datetime.today() + relativedelta(days=1)
        self.assertFalse(initial_start == event.start)
