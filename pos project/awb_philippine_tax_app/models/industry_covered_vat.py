# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IndustryCoveredVat(models.Model):
    _name = "industry.covered.vat"
    _description = "Industry Covered Vat"
    _rec_name = 'awb_name'
    _order = 'awb_name asc'

    awb_name = fields.Char('Name')
    awb_atc_code = fields.Char('ATC Code')
    awb_flag = fields.Boolean(
        compute='check_user_group', string="AWB flag")
    active = fields.Boolean(default=True)

    # @api.depends('awb_flag')
    def check_user_group(self):
        for rec in self:
            if rec.env.user.has_group('awb_philippine_tax_app.admin_Philippine_group_3'):
                rec.awb_flag = True
            else:
                rec.awb_flag = False
