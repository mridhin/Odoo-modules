# -*- coding: utf-8 -*-


from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    discount_name = fields.Char(string='Discount Name')
    discount_amount = fields.Float(string="Discounted Amount")

    @api.model
    def create(self, values):
        values['discount_amount'] = values.get('price_unit') * values.get('discount') / 100
        return super(PosOrderLine, self).create(values)

    @api.model
    def create(self, values):
        order = self.env['pos.order'].search([('id', '=', values.get('order_id'))], limit=1)
        values['discount_name'] = order.discount_name
        return super(PosOrderLine, self).create(values)
