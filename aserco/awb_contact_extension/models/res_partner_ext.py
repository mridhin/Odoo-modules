# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartnerExt(models.Model):
    _inherit = "res.partner"

    is_accredited = fields.Boolean(string='Vendor Accredited', default=False)


