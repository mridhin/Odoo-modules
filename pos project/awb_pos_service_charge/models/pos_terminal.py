from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    service_product_id = fields.Many2one('product.product', string='Service Product')

