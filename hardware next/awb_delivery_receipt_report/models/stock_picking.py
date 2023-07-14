# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#  import from odoo lib
from odoo import models, fields

#Inherited and added new fields for sale order table
class InheritedStockPicking(models.Model):
    _inherit = "stock.picking"
    
    ordered_by = fields.Char('Ordered by', index=True, copy=False, help='ORDERED BY')
    pick_up = fields.Boolean('Pick Up', index=True, copy=False, help='PICK UP')
