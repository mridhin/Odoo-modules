# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sc_id = fields.Char(string='SC ID')
    pwd_id = fields.Char(string='PWD ID')

    