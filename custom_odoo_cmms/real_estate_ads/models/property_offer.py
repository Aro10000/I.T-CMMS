from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError
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
    # ... @api.model#     Must be above Field( creation_date )
    # ... def _set_create_date(self):
    # ...     return fields.Date.today()
    #... creation_date = fields.Date(string='Create Date', default=_set_create_date)
    creation_date = fields.Date(string='Create Date')

    # Step 22-B: Understanding Computed Fields and On-change ORM Decorator
    # This is Understanding Computed Fields
    @api.depends('validity', 'creation_date')# STEP 25-D: Understanding Method Decorators and their Usage: (..@api.depends_context()... optional)
    def _compute_deadline(self):
        for rec in self:
            if rec.creation_date and rec.validity:#                                        Import "from datetime import timedelta " (insert ABOVE) to computer date fields
                rec.deadline = rec.creation_date + timedelta(days=rec.validity)#        You will always get an error trying to directly compute 2 different types of fields....
            else:#                                                                      but use "else" to control computing and stop "errors"
                rec.deadline = False

    def _inverse_deadline(self):
        global rec
        for rec in self:
            if rec.deadline and rec.creation_date:
                rec.validity = (rec.deadline - rec.creation_date).days
        else:
            rec.validity = False

    # STEP 25-A: Understanding Method Decorators and their Usage
    #...@api.autovacuum  # this Decorator deletes "refused" data everyday  ( settings/Schedule Action)
    #...def _cleans_offers(self):
    #...    self.search([('status', '=', 'refused')]).unlink()  # unlink means delete

    # STEP 25-C: Understanding Method Decorators and their Usage: (@api.model_create_multi)
    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            if not rec.get('creation_date'):
                rec['creation_date'] = fields.Date.today()
        return super(PropertOffer, self).create(vals)

    # STEP 25-C: Understanding Method Decorators and their Usage: (..@api.constrains('field')..)
    @api.constrains('validity')
    def _check_validity(self):
        for rec in self:
            if rec.deadline <= rec.creation_date:
                raise ValidationError("Deadline cannot be before creation date")