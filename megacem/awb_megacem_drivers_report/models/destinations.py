# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class Destinations(models.Model):
    _name = "drivers.report.destinations"

    sequence = fields.Integer("Sequence", default=10)
    name = fields.Char("Name")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)



