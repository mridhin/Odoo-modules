# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
# inherit the existing model


class AwbCity(models.Model):
    _name = 'awb.city'

    name = fields.Char(string="Name")
    province_id = fields.Many2one('res.country.state', string="Province")
    zip_code = fields.Integer(string="Zip Code")
    country_id = fields.Char(string="Country", related="province_id.country_id.name")
