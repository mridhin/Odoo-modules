# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    multiple_disc = fields.Char("Discount")

    @api.onchange('multiple_disc')
    def _onchange_multiple_disc(self):
        if self.multiple_disc:
            string_number = self.multiple_disc.replace('/', '')
            if not string_number.isnumeric():
                raise ValidationError(_("The discount format should be something like this 20/10/5"))

    def apply(self):
        for line in self.order_line:
            if self.multiple_disc:
                multiple_disc = self.multiple_disc.replace('/', '%/') + "%"
            else:
                multiple_disc = '0'

            line.discount = line.calculate_disc_from_multiple_disc(multiple_disc)
            line.multiple_disc = multiple_disc

    def remove_discount(self):
        self.apply()

    def distribute_discount(self):
        self.apply()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    multiple_disc = fields.Char("Multiple Disc.%")

    def calculate_disc_from_multiple_disc(self, multiple_disc):
        try:
            # Calculates discounts from multiple discounts
            perc_list = multiple_disc.split("/")
            discounted_price = 0.0
            total_disc = 0.0
            for perc in perc_list:
                disc_perc = float(perc.rstrip("%"))
                price = 100 if discounted_price == 0.0 else discounted_price
                discount_price = price * (disc_perc / 100.0)
                total_disc += discount_price
                discounted_price = price - discount_price
            total_disc_perc = total_disc / 100 * 100
            return round(total_disc_perc, 2)
        except:
            raise ValidationError(_("The Multiple Disc.% format should be something like this 20%/10%/5%"))

    @api.onchange('multiple_disc')
    def _onchange_multiple_disc(self):
        if self.multiple_disc:
            multiple_disc = self.multiple_disc
            self.discount = self.calculate_disc_from_multiple_disc(multiple_disc)

    # Ovverridden in order to update multiple_disc from pricelist to SaleOrderLine
    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('product.group_discount_per_so_line')):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )

        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)

        price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)

        rule = self.env['product.pricelist.item'].browse([rule_id])
        if rule:
            # updating multiple_disc from pricelist' rule to SaleOrderLine
            self.multiple_disc = rule.discounts_computation
        new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                               self.product_uom_qty,
                                                                                               self.product_uom,
                                                                                               self.order_id.pricelist_id.id)

        if new_list_price != 0:
            if self.order_id.pricelist_id.currency_id != currency:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = currency._convert(
                    new_list_price, self.order_id.pricelist_id.currency_id,
                    self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
                self.discount = discount
