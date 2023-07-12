# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class ThNumber(models.Model):
    _inherit = "th.number"

    inventory_count = fields.Integer(string="Inventory count", compute='_compute_inventory_count')

    def _compute_inventory_count(self):
        for rec in self:
            inventory_count = self.env['stock.picking'].search_count([('th_number_ids', '=', rec.id)])
            rec.inventory_count = inventory_count

    def action_count_inventory(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventory',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'domain': [('th_number_ids', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

