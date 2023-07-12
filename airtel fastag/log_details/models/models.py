# -*- coding: utf-8 -*-

from odoo import models, fields, api


class log_details(models.Model):
    _name = "log.details"

    name = fields.Many2one('res.users', string="User Name",readonly=True)
    date = fields.Char(string="Change Date",readonly=True)
    mobile_no = fields.Char(string="Mobile Number Of Changed Person",readonly=True)
    change_from = fields.Char(string="Change From",readonly=True)
    change_to = fields.Char(string="Change To",readonly=True)


class transfer_log_details(models.Model):
    _name = "transfer.details"

    name = fields.Many2one('res.users', string="Deleted User",readonly=True)
    date = fields.Char(string="Date",readonly=True)
    transfer_name = fields.Char(string="Internal Ref No",readonly=True)
    fastag_count = fields.Integer(string="Fastag Count",readonly=True)
    fastag_details_ids = fields.One2many('fastag.details','transfer_details_id',string="Fastag Details",readonly=True)


class fastag_details(models.Model):
    _name = "fastag.details"

    product_barcode = fields.Char(string="Product Barcode")
    transfer_details_id = fields.Many2one('transfer.details')


