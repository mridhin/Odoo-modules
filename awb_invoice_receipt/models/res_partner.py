from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    awb_customer_tin = fields.Char(string='TIN')
    awb_invoice_receipt_business_style = fields.Char(string='Business Style')