# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import ast
#from odoo.addons.coupon.models.coupon import Coupon as base_coupon

class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    maximum_amount = fields.Monetary('Maximum Purchase', 'currency_id')
    maximum_amount_tax_mode = fields.Selection([
        ('incl', 'Included'),
        ('excl', 'Excluded')], default='incl', required=True,
    )
    