# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class ReportStages(models.Model):
    _name = "report.stages"
    _order = "awb_sequence, id"

    awb_sequence = fields.Integer("Sequence", 
        # default value will be 10 + current_number_of_records
        default=lambda self: 10 + self.env['report.stages'].search_count([])
    ) 
    name = fields.Char("Status")
    code = fields.Char("Code")
