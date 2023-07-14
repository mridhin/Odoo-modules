# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class Tax(models.Model):
    _inherit = "account.tax"
    
    awb_tax_description = fields.Char('Tax Description')
    awb_tax_flag = fields.Boolean('Tax Flag Data')
    awb_tax_flag_fields = fields.Boolean(
        compute='check_user_group_flag', string='Tax Flag For Fields')
    awb_Tax_property = fields.Many2one('tax.property',"Tax Property") 
    awb_vat_registration_status = fields.Selection(
            [('unregistered', 'Unregistered'),
            ('registered', 'Registered'),
            ('vat_exempt', 'VAT Exempt'),
            ('all', 'Applicable to All')
            ],string="VAT Registration Status")
    awb_tds = fields.Boolean('EWT', default=False)
    awb_payment_excess = fields.Float('Payment in excess of')
    awb_tds_applicable = fields.Selection([('person', 'Individual'),
                                       ('company', 'Company'),
                                       ('common', 'Common')], string='Applicable to')
    awb_type = fields.Selection(
        [('vat', 'VAT'),('ewt', 'EWT')], string="Type")

    @api.onchange('awb_type','awb_tds_applicable')
    def onchange_type_type(self):
        if self.awb_type == 'ewt':
            return {
                'domain': {'awb_Tax_property': [('awb_type', '=', 'ewt')]}
            }
        if self.awb_type == 'vat':
            return {
                'domain': {'awb_Tax_property': [('awb_type', '=', 'vat')]}
            }


    # def unlink(self):
    #     if self.filtered(lambda awb_tax_flag: awb_tax_flag.awb_tax_flag == True):
    #         raise UserError(
    #             ("You cannot delete this Tax as it is installed by Application."))
    #     return super(Tax, self).unlink()

    @api.depends('awb_tax_flag_fields')
    def check_user_group_flag(self):
        for rec in self:
            if rec.env.user.has_group('awb_philippine_tax_app.acc_Philippine_grouop_2') or rec.env.user.has_group('awb_philippine_tax_app.admin_Philippine_group_3'):
                rec.awb_tax_flag_fields = True
            else:
                rec.awb_tax_flag_fields = False

    @api.model
    def default_get(self, fields):
        res = super(Tax, self).default_get(fields)
        if self.env.user.has_group('awb_philippine_tax_app.acc_Philippine_grouop_2') or self.env.user.has_group('awb_philippine_tax_app.admin_Philippine_group_3'):
            res.update({'awb_tax_flag_fields': True})
        else:
            res.update({'awb_tax_flag_fields': False})
        return res
