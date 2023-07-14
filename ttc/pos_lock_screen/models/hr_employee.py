# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import pytz
import base64


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    login_count = fields.Integer("Max Login Attempt", default=3)
