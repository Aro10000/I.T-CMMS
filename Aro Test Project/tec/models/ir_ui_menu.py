# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if not self.env.user.has_group('tec.group_tec_manager'):
            res.append(self.env.ref('tec.rating_rating_menu_tec').id)
        if self.env.user.has_group('tec.group_tec_stages'):
            res.append(self.env.ref('tec.menu_tecs').id)
            res.append(self.env.ref('tec.menu_tecs_config').id)
        return res
