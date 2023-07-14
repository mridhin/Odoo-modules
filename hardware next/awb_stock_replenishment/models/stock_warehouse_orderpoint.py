from odoo import models, _

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def action_stock_replenishment_locations(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('awb_stock_replenishment.action_stock_replenishment_locations')
        action['name'] = _('Replenishment Location Information for %s', self.product_id.display_name)
        location_lines = []
        stock_quants = self.env['stock.quant'].search([('location_id','!=',self.location_id.id),('product_id','=',self.product_id.id),('on_hand', '=', True)])
        for stock_quant in stock_quants:
            location_line_vals = {
                'stock_location_id' : stock_quant.location_id.id,
                'qty_available':stock_quant.quantity
            }
            location_lines.append((0,0,location_line_vals))
        res = self.env['stock.replenishment.location'].create({
            'orderpoint_id': self.id,
            'product_id': self.product_id.id,
            'location_line':location_lines
        })
        action['res_id'] = res.id
        return action
