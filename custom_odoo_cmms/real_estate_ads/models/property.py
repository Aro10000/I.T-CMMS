
#        Main Model
#        FIRST MODEL
#
#class ModelName(models.Model):
#     _name = 'anyword.modelname'
#     _description = 'Estate Properties'
#
#     field_name = fields.Char(string='Name', required=True)
#     field_name = fields.Text(string='Description')
#     field_name = fields.Char(string='Postcode')
#     field_name = fields.Date(string='Available From')
#     field_name = fields.Float(string='Expected Price')
#     field_name = fields.Float(string='Best Offer')
#     field_name = fields.Float(string='Selling Price')
#     field_name = fields.Integer(string='Bedrooms')
#     field_name = fields.Integer(string='Living Area(sqs)')
#     field_name = fields.Integer(string='Facades')
#     field_name = fields.Boolean(string='Garage', default=False)
#     field_name = fields.Integer(string='Garage Area')
#     field_name = fields.Selection([('north', 'North'), ('north', 'North'),
#                                            ('south', 'South'), ('east', 'East'),
#                                            ('west', 'Wests'),], string='Garage Orientation', default='north')

from odoo import fields, models


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Properties'

    name = fields.Char(string='Name', required=True)
    # Add Many2may(tag_ids) Field To this Model('estate.property') to link with Co-Model('estate.property.tag')
    tag_ids = fields.Many2many('estate.property.tag', string='Property Tag')
    # Add Many2one(type_id) Field To this Model('estate.property') to link with Co-Model('estate.property.type')
    type_id = fields.Many2one('estate.property.type', string='Property Type')
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Available From')
    expected_price = fields.Float(string='Expected Price')
    best_offer = fields.Float(string='Best Offer')
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


#        SECOND MODEL
class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Properties Type'

    name = fields.Char(string='Name', required=True)


#        THIRD MODEL
class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Properties Tag'

    name = fields.Char(string='Name', required=True)

