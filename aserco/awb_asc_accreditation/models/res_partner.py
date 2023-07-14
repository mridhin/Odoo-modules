# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    nature_of_business_industry = fields.Many2one('res.partner.industry', string="Nature of Business")

    products_catered_ids = fields.Many2many('service.offered', relation='accreditations_product_rel',
                                            column1='asc_accreditation_id',
                                            column2='product_id', string='Products Catered',
                                            domain="[('ser_type', '=', 'services')]")
    services_offered_ids = fields.Many2many('service.offered', relation='accreditations_service_rel',
                                            column1='asc_accreditation_id',
                                            column2='service_id', string='Services Offered',
                                            domain="[('ser_type', '=', 'services')]")

    letter_of_intent = fields.Binary(string="Letter of Intent", attachment=True)
    company_profile = fields.Binary(string="Company Profile", attachment=True)
    dti_bnr = fields.Binary(string="DTI Business Name Registration", attachment=True)
    dti_coa = fields.Binary(string="DTI Certificate of Accreditation", attachment=True)
    business_mp = fields.Binary(string="Business / Mayor’s Permit", attachment=True)
    bir_rc = fields.Binary(string="BIR Registration Certificate (Form 2303)", attachment=True)
    orb_si = fields.Binary(string="Scanned copy of Official Receipt and Billing/Service Invoice", attachment=True)
    bac = fields.Binary(string="Brand Accreditation Certificate", attachment=True)
    sec_ai = fields.Binary(string="SEC Article of Incorporation (if corporation)", attachment=True)
    cglip = fields.Binary(string="Comprehensive Gen. Liability Insurance Policy w/ OR", attachment=True)
    pcab = fields.Binary(string="PCAB Contractor’s License", attachment=True)
    cosh_bosch = fields.Binary(string="COSH / BOSCH Training Certificate", attachment=True)
    cpr = fields.Binary(string="Certificate of PHILGEPS Registration", attachment=True)
