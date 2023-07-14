# -*- coding: utf-8 -*-
"""imports from python lib"""
import base64
from datetime import datetime  # @UnusedImport
import barcode # @UnusedImport
from io import BytesIO
import qrcode
import tempfile # @UnusedImport
import shutil # @UnusedImport



"""imports from odoo"""
from odoo import fields, models, api,_  # @UnusedImport



"""Created a class for Awb Compensation Form report. And Variable declaration."""
class AwbFormCompensation(models.Model):
    _name = 'awb.form.compensation'
    _description = "Compensation Form"
    
    name = fields.Char(string="Name")
    bir_form_month = fields.Date()
    barcode_image_text = fields.Char()
    barcode_image = fields.Binary(attachment=True, store=True)
    bir_for_year = fields.Date()
    bir_tin_1 = fields.Char()
    bir_employee = fields.Many2one('res.partner')
    bir_rdo = fields.Char()
    bir_r_address_1 = fields.Char()
    bir_zip_1 = fields.Char()
    bir_local_address = fields.Char()
    bir_zip_2 = fields.Char()
    bir_f_address = fields.Char()
    bir_dob = fields.Date()
    bir_contact = fields.Char()
    bir_min_wage_day = fields.Char()
    bir_min_wage_month = fields.Char()
    bir_mwe = fields.Boolean()
    bir_tin_2 = fields.Char()
    bir_employer = fields.Many2one('res.partner')
    bir_r_address_2 = fields.Char()
    bir_zip_3 = fields.Char()
    bir_main = fields.Boolean()
    bir_secondary = fields.Boolean()
    bir_tin_3 = fields.Char()
    bir_employer_prev = fields.Many2one('res.partner')
    bir_r_address_3 = fields.Char()
    bir_zip_4 = fields.Char()
    bir_gross = fields.Char(compute='_compute_sum_4', store=True)
    bir_less = fields.Char(compute='_compute_sum_5', store=True)
    bir_tax_present = fields.Integer(compute='_compute_sum_6', store=True)
    bir_add = fields.Integer()
    bir_gross_income = fields.Integer(compute='_compute_sum_7', store=True)
    bir_tax_due = fields.Integer()
    bir_present_emp = fields.Integer()
    bir_previous_emp = fields.Integer()
    bir_total_amount_tax = fields.Integer()
    bir_tax_credit = fields.Integer()
    bir_total_tax = fields.Integer()
    bir_for_period_from  = fields.Date()
    bir_for_period_to  = fields.Date()
    bir_basic_sal = fields.Integer()
    bir_h_pay = fields.Integer()
    bir_o_pay = fields.Integer()
    bir_night_shift = fields.Integer()
    bir_har_pay = fields.Integer()
    bir_13th = fields.Integer()
    bir_de_min = fields.Integer()
    bir_sss = fields.Integer()
    bir_sal = fields.Integer()
    bir_total_nontax = fields.Integer()
    bir_basic = fields.Integer()
    bir_representation = fields.Integer()
    bir_transportation = fields.Integer()
    bir_cola = fields.Integer()
    bir_fixed_housing = fields.Integer()
    bir_other_1 = fields.Char()
    bir_other_2 = fields.Integer()
    bir_other_3 = fields.Char()
    bir_other_4 = fields.Integer()
    bir_other_5 = fields.Char()
    bir_other_6 = fields.Integer()
    bir_other_7 = fields.Char()
    bir_other_8 = fields.Integer()
    bir_comission = fields.Integer()
    bir_profit_sharing = fields.Integer()
    bir_fee_dir = fields.Integer()
    bir_tax_13th = fields.Integer()
    bir_har_pay_1 = fields.Integer()
    bir_o_pay_2 = fields.Integer()
    bir_total_tax_income = fields.Integer(compute='_compute_sum_3', store=True)
    bir_a_employer = fields.Binary()
    bir_a_employee = fields.Binary()
    bir_ctc = fields.Char()
    bir_issue = fields.Char()
    
    bir_a_employer_1 = fields.Char()
    bir_date_sign_1 = fields.Date()
    bir_date_sign_2 = fields.Date()
    bir_date_sign_3 = fields.Date()
    bir_amount_ctc = fields.Integer()
    bir_a_employee_1 = fields.Binary()
    logo_bir = fields.Binary()
    
    
    @api.onchange('bir_form_month')
    def generate_barcode(self):
        """qr code generrate function"""
        #if allow only Barcode value
        if self.bir_form_month:
            date = datetime.strftime(self.bir_form_month, '%m%Y' )
            date = date.replace(' ', '/')
            value = '2316'+date+'ENCS'
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(value)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            self.barcode_image = qr_image
            self.barcode_image_text = value
        else:
            self.barcode_image = ''
            
    @api.onchange('bir_present_emp','bir_previous_emp','bir_tax_credit')
    def sum_1(self):
        """ Computation for sum the group of value"""
        self.bir_total_amount_tax = sum([self.bir_present_emp,self.bir_previous_emp])
        self.bir_total_tax = sum([self.bir_total_amount_tax,self.bir_tax_credit])
        
    @api.onchange('bir_basic_sal','bir_h_pay','bir_o_pay',
                  'bir_night_shift','bir_har_pay','bir_13th',
                  'bir_de_min','bir_sss','bir_sal')
    def sum_2(self):
        """ Computation for sum the group of value"""
        self.bir_total_nontax = sum([self.bir_basic_sal,self.bir_h_pay,self.bir_o_pay,
                                     self.bir_night_shift,self.bir_har_pay,self.bir_13th,
                                     self.bir_de_min,self.bir_sss,self.bir_sal])
    
    @api.depends('bir_basic','bir_representation','bir_transportation','bir_cola','bir_fixed_housing',
                 'bir_other_2','bir_other_4','bir_comission','bir_profit_sharing','bir_fee_dir',
                 'bir_tax_13th','bir_har_pay_1','bir_o_pay_2','bir_other_6','bir_other_8')
    def _compute_sum_3(self):
        """ Computation for sum the group of value"""
        self.bir_total_tax_income = sum([self.bir_basic,self.bir_representation,self.bir_transportation,
                                        self.bir_cola,self.bir_fixed_housing,self.bir_other_2,
                                        self.bir_other_4,self.bir_comission,self.bir_profit_sharing,
                                        self.bir_fee_dir,self.bir_tax_13th,self.bir_har_pay_1,
                                        self.bir_o_pay_2,self.bir_other_6,self.bir_other_8])
    
    @api.depends('bir_total_nontax','bir_total_tax_income')
    def _compute_sum_4(self):
        """ Computation for sum the group of value"""
        self.bir_gross = sum([self.bir_total_nontax,self.bir_total_tax_income])
        
    @api.depends('bir_total_nontax')
    def _compute_sum_5(self):
        """ Computation for sum the group of value"""
        self.bir_less = self.bir_total_nontax
        
    @api.depends('bir_less','bir_gross','bir_total_tax_income')
    def _compute_sum_6(self):
        """ Computation for sum the group of value"""
        self.bir_tax_present = (int(self.bir_gross) - int(self.bir_less)) 
        
    @api.depends('bir_tax_present','bir_add')
    def _compute_sum_7(self):
        """ Computation for sum the group of value"""
        self.bir_gross_income = (int(self.bir_tax_present) + int(self.bir_add)) 
        
        
