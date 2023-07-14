from odoo import fields, models, api


class OrderAnalysisLine(models.TransientModel):
    _name = 'order.analysis.line'
    _description = 'Order Analysis Line'
    _rec_name = 'product_id'

    order_id = fields.Many2one('order.analysis','Order')
    product_id = fields.Many2one('product.product','Item Name')
    size = fields.Char('Size')
    qty_ctn = fields.Char('Qty / Ctn')
    inventory_qty = fields.Float('Inventory')
    uom_id = fields.Many2one('uom.uom',string="UOM")
    min = fields.Float('Min')
    max = fields.Float('Max')
    movement_qty = fields.Float('Movement')
    movement_uom_id = fields.Many2one('uom.uom',string="UOM")
    per_day = fields.Float('Per Day')
    ma = fields.Float('M.A. %')


