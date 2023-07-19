# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class ThNumber(models.Model):
    _name = "th.number"

    sequence = fields.Integer("Sequence", default=10)
    name = fields.Char("Name")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    inventory_count = fields.Integer(string="Inventory count", compute="_compute_inventory_count")

    def _compute_inventory_count(self):
        for rec in self:
            inventory_count = self.env['stock.picking'].search_count([('', '', rec.id)])
