# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from lxml import etree
from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_tec_sharing import TestTecSharingCommon


@tagged('post_install', '-at_install')
class TestTecSharingPortalAccess(TestTecSharingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tec_share_wizard = cls.env['tec.share.wizard'].create({
            'access_mode': 'edit',
            'res_model': 'tec.tec',
            'res_id': cls.tec_portal.id,
            'partner_ids': [
                Command.link(cls.partner_portal.id),
            ],
        })
        tec_share_wizard.action_send_mail()

        Task = cls.env['tec.task']
        cls.read_protected_fields_task = OrderedDict([
            (k, v)
            for k, v in Task._fields.items()
            if k in Task.SELF_READABLE_FIELDS
        ])
        cls.write_protected_fields_task = OrderedDict([
            (k, v)
            for k, v in Task._fields.items()
            if k in Task.SELF_WRITABLE_FIELDS
        ])
        cls.readonly_protected_fields_task = OrderedDict([
            (k, v)
            for k, v in Task._fields.items()
            if k in Task.SELF_READABLE_FIELDS and k not in Task.SELF_WRITABLE_FIELDS
        ])
        cls.other_fields_task = OrderedDict([
            (k, v)
            for k, v in Task._fields.items()
            if k not in Task.SELF_READABLE_FIELDS
        ])

    def test_readonly_fields(self):
        """ The fields are not writeable should not be editable by the portal user. """
        view_infos = self.task_portal.get_view(self.env.ref(self.tec_sharing_form_view_xml_id).id)
        fields = [el.get('name') for el in etree.fromstring(view_infos['arch']).xpath('//field[not(ancestor::field)]')]
        tec_task_fields = {
            field_name
            for field_name in fields
            if field_name not in self.write_protected_fields_task
        }
        with self.get_tec_sharing_form_view(self.task_portal, self.user_portal) as form:
            for field in tec_task_fields:
                with self.assertRaises(AssertionError, msg="Field '%s' should be readonly in the tec sharing form view "):
                    form.__setattr__(field, 'coucou')

    def test_read_task_with_portal_user(self):
        self.task_portal.with_user(self.user_portal).read(self.read_protected_fields_task)

        with self.assertRaises(AccessError):
            self.task_portal.with_user(self.user_portal).read(self.other_fields_task)

    def test_write_with_portal_user(self):
        for field in self.readonly_protected_fields_task:
            with self.assertRaises(AccessError):
                self.task_portal.with_user(self.user_portal).write({field: 'dummy'})

        for field in self.other_fields_task:
            with self.assertRaises(AccessError):
                self.task_portal.with_user(self.user_portal).write({field: 'dummy'})
