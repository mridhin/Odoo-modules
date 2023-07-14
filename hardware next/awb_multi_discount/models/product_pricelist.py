# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    enable_multi_disc = fields.Boolean("Enable Multiple Discount")
    discounts_computation = fields.Char("Computation")

    @api.onchange('discounts_computation')
    def _onchange_discounts_computation(self):
        if self.discounts_computation:
            try:
                # Calculates discounts from multiple discounts
                perc_list = self.discounts_computation.split("/")
                discounted_price = 0.0
                total_disc = 0.0
                for perc in perc_list:
                    disc_perc = float(perc.rstrip("%"))
                    price = 100 if discounted_price == 0.0 else discounted_price
                    discount_price = price * (disc_perc / 100.0)
                    total_disc += discount_price
                    discounted_price = price - discount_price
                total_disc_perc = total_disc / 100 * 100
                self.percent_price = round(total_disc_perc, 2)
            except:
                raise ValidationError(_("The computation format should be something like this 20%/10%/5%"))
