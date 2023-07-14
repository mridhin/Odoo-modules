# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.constrains('supplier_taxes_id', 'taxes_id')
    def chck_tax_length(self):
        if len(self.supplier_taxes_id) > 1 or len(self.taxes_id) > 1:
            raise UserError(
                ("You cannot enter more than one tax"))
