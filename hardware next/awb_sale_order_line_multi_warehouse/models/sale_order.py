from odoo import models, fields, api
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_warehouse_id = fields.Many2one('stock.warehouse',
                                           string='Warehouse', help='Warehouses')
    stock_per_warehouse = fields.Integer()

    @api.onchange("name", "product_warehouse_id")
    def onchange_product_warehouse_id(self):
        def get_onhand(warehouse):
            locations = self.env['stock.location'].search([]).filtered(
                lambda x: x.warehouse_id == warehouse and x.usage == 'internal')
            quant = self.env['stock.quant'].search(
                [('product_id', '=', self.product_id.id), ('location_id', 'in', locations.ids)])
            return sum(quant.mapped("quantity"))

        if self.product_warehouse_id:
            self.stock_per_warehouse = get_onhand(self.product_warehouse_id)
        else:
            self.stock_per_warehouse = get_onhand(self.order_id.warehouse_id)

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
             Overwriting the function for adding functionalities of multiple warehouses in the sale order line.

             param previous_product_uom_qty(str): Uom quantity of previous product

             boolean: Returns True, if the picking created.
            """

        if self._context.get("skip_procurement"):
            return True
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.state != 'sale' or not line.product_id.type in (
                    'consu', 'product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty,
                             precision_digits=precision) == 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(
                    line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update(
                        {'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update(
                        {'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)

            # replacing default warehouse_id into product_warehouse_id in the sale order line and adding it into procurement values.

            if line.product_warehouse_id:
                values['warehouse_id'] = line.product_warehouse_id

            product_qty = line.product_uom_qty - qty
            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                product_qty, quant_uom)
            procurements.append(self.env['procurement.group'].Procurement(
                line.product_id, product_qty, procurement_uom,
                line.order_id.partner_shipping_id.property_stock_customer,
                line.product_id.display_name, line.order_id.name,
                line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)
        orders = self.mapped('order_id')
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(
                lambda p: p.state not in ['cancel', 'done'])
            if pickings_to_confirm:
                pickings_to_confirm.action_confirm()
        return True
