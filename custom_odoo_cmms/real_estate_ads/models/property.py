from odoo import fields, models


class Property(models.Model):
    _name = 'estate.property'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Available From')
    expected_price = fields.Float(string='Expected Price')
    selling_price = fields.Float(string='Selling Price')
    bedrooms = fields.Integer(string='Bedrooms')
    living_area = fields.Integer(string='Living Area(sqs)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage', default=False)
    garage_area = fields.Integer(string='Garage Area')
    garage_orientation = fields.Selection([('north', 'North'), ('north', 'North'),
                                           ('south', 'South'), ('east', 'East'),
                                           ('west', 'Wests'),], string='Garage Orientation', default='north')

    # Automatic Fields: id, create_date, create_uid, write_date, write-uid

