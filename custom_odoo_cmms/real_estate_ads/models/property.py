
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

from odoo import fields, models, api


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Properties'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection([('new', 'New'),# STEP 27-A. Actions and Buttons: Working with States and Smart Buttons
                              ('received', 'Offer Received'),
                              ('accepted', 'Offer Accepted'),
                              ('sold', 'Sold'),
                              ('cancel', 'Cancelled')],
                             default='new', string='Status')
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
    garden = fields.Boolean(string='Garden', default=False)
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection([('north', 'North'), ('north', 'North'),
                                           ('south', 'South'), ('east', 'East'),
                                           ('west', 'Wests'),], string='Garage Orientation', default='north')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    sales_id = fields.Many2one('res.users', string='Salesman')
    #STEP 24 B: Creating Related Fields and Applying Domains
    buyer_id = fields.Many2one('res.partner', string="Buyer", domain=[('is_company', '=', True)])
    #
    #STEP 24 A: Creating Related Fields and Applying Domains
    # RULE 1: A related field takes a value based on a Many2one field(EXAMPLE: "buyer_id") that is available in that model(Example "res.partner model") to Reference to another field(EXAMPLE: "phone")
    # RULE 2: "related fields" must be of the same type of field that it was inherited from.
    # RULE 3: "related fields" can only be related to "Many2one Fields"
    phone = fields.Char(string='Phone', related='buyer_id.phone')

    # Automatic Fields: id, create_date, create_uid, write_date, write-uid

    # Step 22: Understanding Computed Fields and On-change ORM Decorator
    # This is Understanding Computed Fields

    #Need to add an "@api Decorator" for the function to work
    @api.depends('living_area', 'garden_area')# Use @api.depends because the computed field("_compute_total_area") is dependant on these 2 fields('living_area', 'garden_area') to work
    def _compute_total_area(self): # Name and define a function
        for rec in self: # for-loop in self
            rec.total_area = rec.living_area + rec.garden_area # These are the fields to be computed: Keep computation simple
            # Also Remember to always keep "function" above the computed field ("total_area")

    #Always put "Compute Fields" below its "Compute Function" when the compute= attribute is not a string
    total_area = fields.Integer(string='Total Area', compute=_compute_total_area)# Always use the "Compute" Attribute: for Compute Fields

    def action_sold(self):# STEP 27-D. Actions and Buttons: Working with States and Smart Buttons -->
        self.state = 'sold'
    def action_cancel(self):# STEP 27-D. Actions and Buttons: Working with States and Smart Buttons -->
        self.state = 'cancel'

    @api.depends('offer_ids')# STEP 27-H. Actions and Buttons: Working with States and Smart Buttons -->
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    offer_count = fields.Integer(string="Offer Count", compute=_compute_offer_count)


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
    color = fields.Integer(string='Color')

