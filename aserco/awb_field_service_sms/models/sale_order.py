# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import re
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.constrains('x_studio_contact_no_1')
    def check_phone_number(self):
        for rec in self:
            if rec.x_studio_contact_no_1:
                pattern = '(^[+63]{3})([0-9]{10})'
                result = re.match(pattern, rec.x_studio_contact_no_1)
                if not result:
                    raise UserError(_('Contact number format is not accepted. You either have space between number '
                                      'or phone number does not starts from +63'))