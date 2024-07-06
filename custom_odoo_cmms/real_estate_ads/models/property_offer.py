from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError


# Types of MODELS
# Abstract, Transient, Regular Model

#class AbstractOffer(models.AbstractModel):#29. Understanding Wizards and Generic Models: TransientModel and AbstractModel
    #_name = 'abstract.model.offer'
    #_description = 'Abstract Offers'

    #partner_email = fields.Char(string='Email')
    #partner_phone = fields.Char(string='Phone Number')


#        Forth MODEL
class PropertOffer(models.Model):
    _name = 'estate.property.offer'
    #_inherit = ['abstract.model.offer']#29. Understanding Wizards and Generic Models: TransientModel and AbstractModel
    _description = 'Estate Properties offer'

    @api.depends('property_id', 'partner_id')# STEP 27-F. Actions and Buttons: Working with States and Smart Buttons -->
    def _compute_name(self):
        for rec in self:
            if rec.property_id and rec.partner_id:
                rec.name = f'{rec.property_id.name} - {rec.partner_id.name}'
            else:
                rec.name = False

    name = fields.Char(string='Description', compute=_compute_name)# STEP 27-F. Actions and Buttons: Working with States and Smart Buttons -->
    price = fields.Float(string='Price', required=True)
    status = fields.Selection([('accepted', 'Accepted'),
                               ('refused', 'Refused'),], string='status')
    partner_id = fields.Many2one('res.partner', string='Customer')
    property_id = fields.Many2one('estate.property', string='Property')
    validity = fields.Integer(string='Validity (days)', default=7)
    deadline = fields.Date(string='Deadline', compute='_compute_deadline', inverse='_inverse_deadline')# Always use Compute And Inverse Attributes: for Compute And Inverse Fields

    # STEP 25B: Understanding Method Decorators and their Usage: (@api.model Decorator)
    @api.model  # Must be above Field( creation_date )
    def _set_create_date(self):#35. [EXTRA] Understanding Attrs, Sequence and Widgets Available in Odoo-->
        return fields.Date.today()

    creation_date = fields.Date(string='Create Date', default=_set_create_date)#35. [EXTRA] Understanding Attrs, Sequence and Widgets Available in Odoo-->
    #creation_date = fields.Date(string='Create Date')

    # Step 22-B: Understanding Computed Fields and On-change ORM Decorator
    # This is Understanding Computed Fields
    @api.depends('validity', 'creation_date')# STEP 25-D: Understanding Method Decorators and their Usage: (..@api.depends_context()... optional)
    def _compute_deadline(self):
        for rec in self:
            if rec.creation_date and rec.validity:#                                        Import "from datetime import timedelta " (insert ABOVE) to computer date fields
                rec.deadline = rec.creation_date + timedelta(days=rec.validity)#        You will always get an error trying to directly compute 2 different types of fields....
            else:#                                                                      but use "else" to control computing and stop "errors"
                rec.deadline = False

    def _inverse_deadline(self):# Step 22-B: Understanding Computed Fields and On-change ORM Decorator
        for rec in self:
            if rec.deadline and rec.creation_date:
                rec.validity = (rec.deadline - rec.creation_date).days
        #else:
            #rec.validity = False

    # STEP 25-A: Understanding Method Decorators and their Usage
    #...@api.autovacuum  # this Decorator deletes "refused" data everyday  ( settings/Schedule Action)
    #...def _cleans_offers(self):
    #...    self.search([('status', '=', 'refused')]).unlink()  # unlink means delete

    # STEP 25-C: Understanding Method Decorators and their Usage: (@api.model_create_multi)
    #@api.model_create_multi
    #def create(self, vals):
        #for rec in vals:
            #if not rec.get('creation_date'):
               # rec['creation_date'] = fields.Date.today()
        #return super(PropertOffer, self).create(vals)

    # STEP 25-E: Understanding Method Decorators and their Usage: (..@api.constrains('field')..)
    @api.constrains('validity')
    def _check_validity(self):
        for rec in self:
            if rec.deadline <= rec.creation_date:
                raise ValidationError("Deadline cannot be before creation date")

    #35. [EXTRA] Understanding Attrs, Sequence and Widgets Available in Odoo-->
    def action_accept_offer(self):#35. [EXTRA] Understanding Attrs, Sequence and Widgets Available in Odoo-->
        if self.property_id:
            self.property_id.write({
                'selling_price': self.price# This LOGIC is to allow "Accepted button" to Automatically update "Selling Price" When Selected or Click.
            })
        self.status = 'accepted'

    def action_decline_offer(self):#35. [EXTRA] Understanding Attrs, Sequence and Widgets Available in Odoo-->
        self.status = 'refused'