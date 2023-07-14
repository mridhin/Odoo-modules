from odoo import fields, models, api
from odoo.exceptions import ValidationError

class OrderAnalysis(models.TransientModel):
    _name = 'order.analysis'
    _description = 'Order Analysis'
    _rec_name = 'product_name'

    product_name = fields.Char('Item Name', required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    line_ids = fields.One2many('order.analysis.line','order_id',string="Lines")

    def generate(self):
        print(self)
        lines = self.generate_lines()
        self.line_ids.unlink()
        self.line_ids =  lines

    def generate_lines(self):
        lines = []
        products = self.env['product.product'].search([('name','ilike',self.product_name)])
        total_purchase_qty_obj =  self.env['purchase.order.line'].read_group(domain = [('product_id', 'in', products.ids),('order_id.date_order','>=',self.start_date),('order_id.date_order','<=',self.end_date)],fields = ['product_qty'], groupby = ['product_id'])
        print(total_purchase_qty_obj)
        for product in products:
            diff_days = self.end_date - self.start_date
            if diff_days.days < 0:
                raise ValidationError('From Date should not be less then end date')

            purchase_qty = self.env['purchase.order.line'].read_group(domain = [('product_id', '=', product.id),('order_id.date_order','>=',self.start_date),('order_id.date_order','<=',self.end_date)],fields = ['product_qty'], groupby = ['product_id'])
            print(purchase_qty)
            movement_qty = 0
            per_day = 0
            ma = 0
            qty_ctn = ''
            if purchase_qty:
                movement_qty = purchase_qty[0]['product_qty']
                per_day = movement_qty / diff_days.days
                total_purchase_qty = total_purchase_qty_obj[0]['product_qty']
                print(total_purchase_qty)
                print(per_day)
                ma = per_day / total_purchase_qty * 100


            line_vals = {
                'product_id':product.id,
                'size':product.product_tmpl_id.x_studio_size_or_id,
                'qty_ctn':qty_ctn,
                'inventory_qty':product.qty_available,
                'uom_id':product.uom_id.id,
                'min':0,
                'max':0,
                'movement_qty':movement_qty,
                'movement_uom_id':product.uom_id.id,
                'per_day':per_day,
                'ma':ma

            }
            lines.append((0,0,line_vals))

        return lines
