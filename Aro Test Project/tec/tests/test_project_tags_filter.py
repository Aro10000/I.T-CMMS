# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged, HttpCase
from odoo import Command
from .test_tec_base import TestTecCommon


@tagged('-at_install', 'post_install')
class TestTecTags(HttpCase, TestTecCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['tec.tags'].create([
            {'name': 'Corkscrew tailed', 'tec_ids': [Command.link(cls.tec_pigs.id)]},
            {'name': 'Horned', 'tec_ids': [Command.link(cls.tec_goats.id)]},
            {
                'name': '4 Legged',
                'tec_ids': [
                    Command.link(cls.tec_goats.id),
                    Command.link(cls.tec_pigs.id),
                ],
            },
        ])

        cls.tec_pigs.write({
            'stage_id': cls.env['tec.tec.stage'].create({
                'name': 'pig stage',
            }).id,
        })
        cls.tec_goats.write({
            'stage_id': cls.env['tec.tec.stage'].create({
                'name': 'goat stage',
            }).id,
        })

        cls.env["res.config.settings"].create({'group_tec_stages': True}).execute()

        cls.env['ir.filters'].create([
            {
                'name': 'Corkscrew tail tag filter',
                'model_id': 'tec.tec',
                'domain': '[("tag_ids", "ilike", "Corkscrew")]',
            },
            {
                'name': 'horned tag filter',
                'model_id': 'tec.tec',
                'domain': '[("tag_ids", "ilike", "horned")]',
            },
            {
                'name': '4 Legged tag filter',
                'model_id': 'tec.tec',
                'domain': '[("tag_ids", "ilike", "4 Legged")]',
            },
        ])

    def test_01_tec_tags(self):
        self.start_tour("/web", 'tec_tags_filter_tour', login="admin")
