from odoo import api, fields, models, _
# from mako.pyparser import reserved
import json
from odoo.exceptions import UserError, ValidationError

class Consult(models.Model):
    _name = "asc.accreditation"
    _description = "ASC accreditation"
    
   
#fields in form page 
    name =  fields.Char(string='Name')
    email =  fields.Char(string='E-Mail')
    mob_no = fields.Text(default='9')
    city =  fields.Char(string='City')
    name_of_bs =  fields.Char(string='Nature of Business')
    products = fields.Many2many('service.offered', relation='accreditation_products_rel', column1='accreditation_id', column2='product_id', string='Products')
    ser_off =  fields.Many2many('service.offered',relation='accreditation_services_rel', column1='accreditation_id', column2='service_id', string='Services Offered')
    file = fields.Binary ( 'File' , help = "File to check and / or import" )
    
 


            
