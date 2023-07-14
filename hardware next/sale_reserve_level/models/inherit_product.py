# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import api, fields, models, _
"""imports from python lib"""
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError

"""inherit the base class and add a field"""
class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    
    res_level = fields.Char(string='Reserve Level')


"""inherit the base class and add a conditions"""
class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    
    # cus_type = fields.Char(string='Customer Type')
    
    
    #Check the when create a method for the x_studio_customer_type_1 field and product_uom_qty fields values
    @api.model
    def create(self, vals):
        if vals.get('x_studio_customer_type_1') == 'WS':
            for line in vals.get('order_line'):
                product = self.env['product.product'].browse(line[2]['product_id'])
                if product.res_level and line[2]['product_uom_qty'] >= int(product.res_level):
                    raise ValidationError("Sorry, item is on reserve level.")
        return super(SaleOrder, self).create(vals)


    #Check the when write a method for the x_studio_customer_type_1 field and product_uom_qty fields values
    def write(self, vals):
        if vals.get('x_studio_customer_type_1') == 'WS':
            for line in self.order_line:
                new_qty = vals.get('order_line')[0][2].get('product_uom_qty')
                if  vals.get('x_studio_customer_type_1') == 'WS' and new_qty >= int(line.product_id.res_level):
                    raise ValidationError("Sorry, item is on reserve level.")
        return super(SaleOrder, self).write(vals)


    #Check the when onchange a method for the x_studio_customer_type_1 field and product_uom_qty fields values
    @api.onchange('order_line')
    def onchange_order_line(self):
        for line in self.order_line:
            product = line.product_id
            if product.res_level and line.product_uom_qty >= int(product.res_level) and self.x_studio_customer_type_1 == 'WS':
                raise ValidationError("Sorry, item is on reserve level.")

    