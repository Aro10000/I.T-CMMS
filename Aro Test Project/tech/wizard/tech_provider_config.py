# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.addons.base.models.ir_module import assert_log_admin_access


class TechProviderConfig(models.TransientModel):
    _name = 'tech.provider.config'
    _description = 'Tech Provider Configuration Wizard'

    external_tech_provider = fields.Selection([
        ('google', 'Google'), ('microsoft', 'Outlook')],
        "Choose an external tech to configure", default='google')

    # Allow to sync with eventually existing ICP keys without creating them if respective module is not installed
    # Using same field names and strings as their respective res.config.settings
    cal_client_id = fields.Char(
        "Google Client_id",
        default=lambda self: self.env['ir.config_parameter'].get_param('google_tech_client_id'))
    cal_client_secret = fields.Char(
        "Google Client_key",
        default=lambda self: self.env['ir.config_parameter'].get_param('google_tech_client_secret'))
    microsoft_outlook_client_identifier = fields.Char(
        "Outlook Client Id",
        default=lambda self: self.env['ir.config_parameter'].get_param('microsoft_tech_client_id'))
    microsoft_outlook_client_secret = fields.Char(
        "Outlook Client Secret",
        default=lambda self: self.env['ir.config_parameter'].get_param('microsoft_tech_client_secret'))

    @assert_log_admin_access
    def action_tech_prepare_external_provider_sync(self):
        """ Called by the wizard to configure an external tech provider without requiring users
        to access the general settings page.
        Make sure that the provider tech module is installed or install it. Then, set
        the API keys into the applicable config parameters.
        """
        self.ensure_one()
        tech_module = self.env['ir.module.module'].search([
            ('name', '=', f'{self.external_tech_provider}_tech')])

        if tech_module.state != 'installed':
            tech_module.button_immediate_install()

        if self.external_tech_provider == 'google':
            self.env['ir.config_parameter'].set_param('google_tech_client_id', self.cal_client_id)
            self.env['ir.config_parameter'].set_param('google_tech_client_secret', self.cal_client_secret)
        elif self.external_tech_provider == 'microsoft':
            self.env['ir.config_parameter'].set_param('microsoft_tech_client_id', self.microsoft_outlook_client_identifier)
            self.env['ir.config_parameter'].set_param('microsoft_tech_client_secret', self.microsoft_outlook_client_secret)
