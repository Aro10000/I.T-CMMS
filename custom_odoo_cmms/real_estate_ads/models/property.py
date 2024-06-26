from odoo import fields, models


class Property(models.Model):
    -name = 'estate.property'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Date')
    expected_price = fields.Float(string='Expected Price')
