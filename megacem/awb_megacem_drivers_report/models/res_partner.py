# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    dr_count = fields.Integer(string="DR Count", compute='_compute_dr_count')

    def _compute_dr_count(self):
        for rec in self:
            dr_count = self.env['drivers.report'].search_count([('customer', '=', rec.id)])
            rec.dr_count = dr_count

    def action_count_dr(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Drivers Report',
            'res_model': 'drivers.report',
            'view_type': 'form',
            'domain': [('customer', '=', self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
