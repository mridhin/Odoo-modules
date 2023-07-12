# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    driver_report_id = fields.Many2one('drivers.report', string="Driver Report")
    is_driver_report = fields.Boolean()
