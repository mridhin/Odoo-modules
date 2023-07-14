# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    awb_vat_registration_status = fields.Selection([
        ('unregistered', 'Unregistered'),
        ('registered', 'Registered'),
        ('vat_Exempt', 'VATExempt'),
    ], string="VAT Registration Status", default='unregistered')
    awb_first_name = fields.Char('First Name')
    awb_middle_name = fields.Char('Middle Name')
    awb_last_name = fields.Char('Last Name')
    awb_vat_registration_no = fields.Char('VAT Registration No')
    awb_industries_id = fields.Many2one(
        'industry.covered.vat', string='Industries Covered By VAT')
    awb_business_style = fields.Char('Business Style')
    awb_default_customer_taxes_id = fields.Many2one(
        'account.tax', string='Default Customer VAT')
    awb_default_vendor_taxes_id = fields.Many2one(
        'account.tax', 'Default Vendor VAT')
    awb_flag = fields.Boolean(
        compute='check_user_group', string="AWB flag")
    awb_default_customer_ewt_id = fields.Many2one(
        'account.tax', string='Default Customer EWT')
    awb_default_vendor_ewt_id = fields.Many2one(
        'account.tax', 'Default Vendor EWT')
    tds_threshold_check = fields.Boolean(string='Check WET Threshold', default=True)

    awb_street = fields.Char("Street")
    awb_street2 = fields.Char("Street2")
    awb_city = fields.Char("City")
    awb_state_id = fields.Many2one('res.country.state','State')
    awb_zip = fields.Char("Zip")
    awb_country_id = fields.Many2one('res.country','Country')
    
    @api.depends('awb_flag')
    def check_user_group(self):
        for rec in self:
            if rec.env.user.has_group('awb_philippine_tax_app.acc_Philippine_grouop_2') or rec.env.user.has_group('awb_philippine_tax_app.admin_Philippine_group_3'):
                rec.awb_flag = True
            else:
                rec.awb_flag = False

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        if self.env.user.has_group('awb_philippine_tax_app.acc_Philippine_grouop_2') or self.env.user.has_group('awb_philippine_tax_app.admin_Philippine_group_3'):
            res.update({'awb_flag': True})
        else:
            res.update({'awb_flag': False})
        return res
