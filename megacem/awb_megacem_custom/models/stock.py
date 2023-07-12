from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    check_received_employee_id = fields.Many2one('hr.employee')
    noted_employee_id = fields.Many2one('hr.employee')


class StockMove(models.Model):
    _inherit = "stock.move"
    
    price_unit = fields.Float(string='Unit Price', digits='Product Price')

