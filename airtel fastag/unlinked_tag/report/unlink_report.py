from odoo import models, fields, api,_

class unlinked_tag_report(models.Model):
    _name = 'unlinked.report'
    _description = 'unlinked report'

    name = fields.Char(string='Txn date')
    month = fields.Char(string="Month")
    tag_id = fields.Char(string='Tag ID')
    bar_code = fields.Char(string='Barcode No')
    amount = fields.Char(string='Amount')
    toll_plaza = fields.Char(string='Toll Plaza')
    circle_id = fields.Many2one('rs.circle.name', string="Circle")
    product_assign_to = fields.Many2one('res.users', string="Product Assign To")
    employee_id = fields.Char(string="Employee ID")
    product_unlink_by = fields.Many2one('res.users', string="Product Unlink By")