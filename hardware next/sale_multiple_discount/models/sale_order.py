# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # multiple_disc = fields.Char('Discount')

    # This onchange function is a duplication of the onchange function available in awb_multi_discount, also the validation message is not working
    # @api.onchange('multiple_disc')
    # def _onchange_multiple_disc(self):
    #     for line in self:
    #         print('--------==>>> line.multiple_disc', line.multiple_disc)
    #         if line.multiple_disc:
    #             # try:
    #                 # Calculates discounts from multiple discounts
    #             price = line.price_unit
    #             multiple_disc = re.sub(r'[^a-zA-Z0-9 .-]',r'-',line.multiple_disc)
    #             multiple_disc = re.sub(r'\s+', '-', multiple_disc)
    #             discount_list = multiple_disc.split('-')
    #             discount_list = list(filter(None, discount_list))
    #             discounted_price = 0.0
    #             total_disc = 0.0
    #             for discount in discount_list:
    #                 disc_perc = float(discount)
    #                 price = 100 if discounted_price == 0.0 else discounted_price
    #                 discount_price = price * (disc_perc / 100.0)
    #                 total_disc += discount_price
    #                 discounted_price = price - discount_price
    #             total_disc_perc = total_disc / 100 * 100
    #             line.discount = round(total_disc_perc, 2)
    #         else:
    #             line.discount = 0.0

    # @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'multiple_disc')
    # def _compute_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         multiple_disc = ''
    #         if line.multiple_disc:
    #             price = line.price_unit
    #             multiple_disc = re.sub(r'[^a-zA-Z0-9 .-]',r'-',line.multiple_disc)
    #             multiple_disc = re.sub(r'\s+', '-', multiple_disc)
    #             discount_list = multiple_disc.split('-')
    #             discount_list = list(filter(None, discount_list))
    #             for discount in discount_list:
    #                 price = price * (1 - (float(discount) or 0.0) / 100.0)
    #         else:
    #             price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         print('--------==>>> price', price)
    #         taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
    #         print('--------==>>> taxes', taxes)
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })