# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import users

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.tec.tests.test_tec_base import TestTecCommon

@tagged('-at_install', 'post_install')
class TestTecUpdateAccessRights(TestTecCommon):
    @classmethod
    def setUpClass(cls):
        super(TestTecUpdateAccessRights, cls).setUpClass()
        cls.tec_update_1 = cls.env['tec.update'].create({
            'name': "Test Tec Update",
            'tec_id': cls.tec_pigs.id,
            'status': 'on_track',
        })
        cls.tec_milestone = cls.env['tec.milestone'].create({
            'name': 'Test Projec Milestone',
            'tec_id': cls.tec_pigs.id,
        })
        cls.base_user = mail_new_test_user(cls.env, 'Base user', groups='base.group_user')
        cls.tec_user = mail_new_test_user(cls.env, 'Tec user', groups='tec.group_tec_user')
        cls.tec_manager = mail_new_test_user(cls.env, 'Tec admin', groups='tec.group_tec_manager')
        cls.portal_user = mail_new_test_user(cls.env, 'Portal user', groups='base.group_portal')

    @users('Tec user', 'Tec admin', 'Base user')
    def test_tec_update_user_can_read(self):
        self.tec_update_1.with_user(self.env.user).name

    @users('Base user')
    def test_tec_update_user_no_write(self):
        with self.assertRaises(AccessError, msg="%s should not be able to write in the tec update" % self.env.user.name):
            self.tec_update_1.with_user(self.env.user).name = "Test write"

    @users('Tec admin')
    def test_tec_update_admin_can_write(self):
        self.tec_update_1.with_user(self.env.user).name = "Test write"

    @users('Base user')
    def test_tec_update_user_no_unlink(self):
        with self.assertRaises(AccessError, msg="%s should not be able to unlink in the tec update" % self.env.user.name):
            self.tec_update_1.with_user(self.env.user).unlink()

    @users('Tec admin')
    def test_tec_update_admin_unlink(self):
        self.tec_update_1.with_user(self.env.user).unlink()

    @users('Portal user')
    def test_tec_update_portal_user_no_read(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to read in the tec update"):
            self.tec_update_1.with_user(self.env.user).name

    @users('Portal user')
    def test_tec_update_portal_user_no_write(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to write in the tec update"):
            self.tec_update_1.with_user(self.env.user).name = 'Test write'

    @users('Portal user')
    def test_tec_update_portal_user_no_create(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to create in the tec update model"):
            self.env['tec.update'].with_user(self.env.user).create({
                'name': 'Test Create with portal user',
                'tec_id': self.tec_pigs.id,
                'state': 'on_track',
            })

    @users('Portal user')
    def test_tec_update_portal_user_no_unlink(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to unlink in the tec update"):
            self.tec_update_1.with_user(self.env.user).unlink()

    @users('Portal user')
    def test_tec_milestone_portal_user_no_read(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to read in the tec update"):
            self.tec_milestone.with_user(self.env.user).name

    @users('Portal user')
    def test_tec_milestone_portal_user_no_write(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to write in the tec update"):
            self.tec_milestone.with_user(self.env.user).name = 'Test write'

    @users('Portal user')
    def test_tec_milestone_portal_user_no_create(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to create in the tec update model"):
            self.env['tec.update'].with_user(self.env.user).create({
                'name': 'Test Create with portal user',
                'tec_id': self.tec_pigs.id,
            })

    @users('Portal user')
    def test_tec_milestone_portal_user_no_unlink(self):
        with self.assertRaises(AccessError, msg=f"{self.env.user.name} should not be able to unlink in the tec update"):
            self.tec_milestone.with_user(self.env.user).unlink()
