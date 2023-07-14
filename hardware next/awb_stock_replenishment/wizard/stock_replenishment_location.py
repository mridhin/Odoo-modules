# -*- coding: utf-8 -*-

from odoo import fields, models

class StockReplenishmentLocation(models.TransientModel):
    _name = 'stock.replenishment.location'
    _description = 'Stock supplier replenishment location'
    _rec_name = 'orderpoint_id'

    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint')
    product_id = fields.Many2one('product.product', related='orderpoint_id.product_id')
    location_line = fields.One2many('stock.replenishment.location.line','location_id','Location Lines')

class StockReplenishmentLocationLine(models.TransientModel):
    _name = 'stock.replenishment.location.line'
    _description = 'Stock supplier replenishment location'
    _rec_name = 'location_id'
    _order = 'qty_available asc'

    location_id = fields.Many2one('stock.replenishment.location')
    stock_location_id = fields.Many2one('stock.location','Location')
    qty_available = fields.Float('On Hand')
