# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#  import from odoo lib
from odoo import models, fields 

#create a new class and to add new field
class ResPartnerDeliveryArea(models.Model):
    _name = 'res.partner.delivery.area'
    _description = 'res partner delivery area'
    
    name = fields.Char('Delivery Area')