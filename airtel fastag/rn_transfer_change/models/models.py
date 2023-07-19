# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class rn_transfer_change(models.Model):
#     _name = 'rn_transfer_change.rn_transfer_change'
#     _description = 'rn_transfer_change.rn_transfer_change'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()

#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"
    
    
 
# class StockMove(models.Model):
#     _inherit = "stock.move"
    



class ProductProduct(models.Model):
    _inherit = "product.product"
    vehical_type=fields.Many2one('product.category',string='Vehical Type ',required=True)
    tag_id = fields.Char(string="Tag ID",required=True)
    assign_to_mob= fields.Char(string='Assign to Mob')
    fastag_sold = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                   string="Sold", default='no')
    rs_faulty_stag = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                      string="Faulty", default='no')
    unlink_fastag = fields.Boolean(string="Unlink")
    unlink_amount = fields.Integer(string="Unlink amount")
    tag_color = fields.Many2many('res.partner.category',string="Tag Color")
    rs_tag_id = fields.Char(string="Vehicle Type ID")
    upload_date = fields.Date(string="uploaded Date")
    vendor_name = fields.Many2one('res.partner', string="Vendor Name")
    assigned_To = fields.Many2many('res.users',string="Assigned To ")
    vendor_id = fields.Integer(string="Vendor ID")
    employee_no = fields.Char(string="Employee No")