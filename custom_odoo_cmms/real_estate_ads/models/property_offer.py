from odoo import fields, models, api
from datetime import timedelta

#        Forth MODEL
class PropertOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Properties offer'

    price = fields.Float(string='Price', required=True)
    status = fields.Selection([('accepted', 'Accepted'),
                               ('refuse', 'Refused'),], string='status')
    partner_id = fields.Many2one('res.partner', string='Customer')
    property_id = fields.Many2one('estate.property', string='Property')
    validity = fields.Integer(string='Validity (days)')
    deadline = fields.Date(string='Deadline', compute='_compute_deadline', inverse='_inverse_deadline')# Always use Compute And Inverse Attributes: for Compute And Inverse Fields

    # STEP 25B: Understanding Method Decorators and their Usage: (@api.model Decorator)
    @api.model
    def _set_create_date(self):
        return fields.Date.today()
    creation_date = fields.Date(string='Create Date', default=_set_create_date)

    # Step 22B: Understanding Computed Fields and On-change ORM Decorator
    # This is Understanding Computed Fields
    @api.depends('validity', 'creation_date')
    def _compute_deadline(self):
        for rec in self:
            if rec.creation_date and rec.validity:#                                     Import "from datetime import timedelta " (insert ABOVE) to computer date fields
                rec.deadline = rec.creation_date + timedelta(days=rec.validity)#        You will always getan error trying to directly compute 2 differebt types of fields....
            else:#                                                                      but use "else" to control computing and stop "errors"
                rec.deadline = False

    def _inverse_deadline(self):
        for rec in self:
            rec.validity = (rec.deadline - rec.creation_date).days

    # STEP 25A: Understanding Method Decorators and their Usage
    #...@api.autovacuum  # this Decorator deletes "refused" data everyday  ( settings/Schedule Action)
    #...def _cleans_offers(self):
    #...    self.search([('status', '=', 'refused')]).unlink()  # unlink means delete

