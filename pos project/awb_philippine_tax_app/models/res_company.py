# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    awb_vat_registration_status = fields.Selection([
        ('unregistered', 'Unregistered'),
        ('registered', 'Registered'),
        ('vat_Exempt', 'VATExempt'),
    ], string="VAT Registration Status", default='unregistered')
    awb_vat_registration_no = fields.Char('VAT Registration No')
    awb_line_of_business = fields.Char('Line of Business')
    awb_business_style = fields.Char('Business Style')
    awb_rdo_name = fields.Char('RDO Name')
    awb_rdo_code = fields.Char('RDO Code')

    awb_street = fields.Char("Street")
    awb_street2 = fields.Char("Street2")
    awb_city = fields.Char("City")
    awb_state_id = fields.Many2one('res.country.state','State')
    awb_zip = fields.Char("Zip")
    awb_country_id = fields.Many2one('res.country','Country')
    awb_category_of_withholding_agent = fields.Selection(
        [('private', 'Private'), ('government', 'Government')], 'Category of Withholding Agent')
    awb_top_withholding_agent = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], 'Top Withholding Agent?')
