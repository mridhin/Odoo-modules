# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError

class SaleTeamPrefix(models.Model):
    _name = "sale.team.prefix"

    name = fields.Char(string='Sales Team Prefix for sequence', copy=False)
 
    _sql_constraints = [
    ('sales_team_prefix_uniq', 'unique (name)',
        " A sales team already exists with same prefix. Please choose another prefix.")
    ]

    @api.constrains('name')
    def _check_name(self):
        if not self.name:
            """
                If name is blank/whitespace, throw an error.
            """
            raise UserError("Invalid sales team prefix.")