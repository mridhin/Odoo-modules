from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dr_doc_no = fields.Char('TDS/RS No.')
