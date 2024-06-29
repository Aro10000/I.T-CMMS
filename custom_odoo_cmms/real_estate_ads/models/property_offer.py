from odoo import fields, models

#        Forth MODEL
class PropertOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Properties offer'

    price = fields.Float(string='Price', required=True)
    status = fields.Selection([('accepted', 'Accepted'),
                               ('refuse', 'Refused'),], string='status')
    partner_id = fields.Many2one('res.partner', string='Customer')
    property_id = fields.Many2one('estate.property', string='Property')
