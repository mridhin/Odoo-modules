# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    awb_vat_registration_status = fields.Selection([
        ('unregistered', 'Unregistered'),
        ('registered', 'Registered'),
        ('vat_Exempt', 'VATExempt'),
    ], default='unregistered', string="VAT Registration Status")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id:
            self.awb_vat_registration_status = self.partner_id.awb_vat_registration_status
        else:
            self.awb_vat_registration_status = 'unregistered'


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.constrains('taxes_id')
    def chck_tax_length(self):
        for line in self:
            if len(line.taxes_id) > 1:
                raise UserError(
                    ("You cannot enter more than one tax"))
