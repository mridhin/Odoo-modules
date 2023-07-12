# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class BulkNumber(models.Model):
    _name = "bulk.number"

    name = fields.Char("Name")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _sql_constraints = [
    ('name_uniq', 'UNIQUE (name)', 'Bulk Number/Plate Number should not be duplicated!')
]