# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ProductSupplierinfo(models.Model):
   _inherit = 'product.supplierinfo'

   product_supplierinfo_line_ids = fields.One2many('product.supplierinfo.line', 'product_supplierinfo_id', string='Supplier info line')


class ProductSupplierinfoLine(models.Model):
    _name = 'product.supplierinfo.line'

    product_supplierinfo_id = fields.Many2one('product.supplierinfo', string='Supplier Info')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description', required=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    #taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    price_subtotal = fields.Float(string='Subtotal')