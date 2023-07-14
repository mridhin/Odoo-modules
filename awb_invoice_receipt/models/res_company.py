from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    acknowledgement_certificate = fields.Char(string='Acknowledgement Certificate No.')
    certificate_date_issued = fields.Datetime(string='Date Issued')
    series_range = fields.Char(string='Series Range')

    awb_invoice_receipt_business_style = fields.Char('Business Style')