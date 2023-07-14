# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError
import datetime
import calendar


class E2307(models.Model):
    _name = "e.2307"
    _description = "0619E"
    _rec_name = 'awb_company_id'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    awb_company_id = fields.Many2one('res.company', string='Company')
    awb_partner_id = fields.Many2one('res.partner', string='Partner')
    awb_journal_id = fields.Many2one('account.journal', string='Journal')
    awb_fiscal_year = fields.Many2one(
        'account.fiscal.year', string='Fiscal Year')
    awb_fiscal_quarter = fields.Many2one(
        'account.month.period', string='Fiscal Quarter')
    awb_month = fields.Char('Month')
    awb_year = fields.Char('Year')
    awb_entry_count = fields.Boolean(
        'Entry Count', default=False, compute='check_journal_entry')
    awb_move_id = fields.Many2one('account.move',
                                  string='Journal Entry',
                                  )
    awb_amended_return = fields.Selection(
        [('t', 'Yes'), ('f', 'No')], 'Amended Return?', default='f')
    awb_short_period_return = fields.Selection(
        [('tru', 'Yes'), ('fal', 'No')], 'Short Period Return', default='tru')
    awb_no_of_Sheets = fields.Integer('Sheets Attached')
    awb_special_tax_or_inter_tax_treaty = fields.Selection(
        [('y', 'Yes'), ('n', 'No')],
        string='tax relief under Special Law or International Tax Treaty', default='n')
    awb_specify = fields.Char('If Yes, please specify')
    awb_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('amendment', 'Amendment')], tracking=True,
        required=True, readonly=True, default='draft', copy=False)
    awb_barcode = fields.Char("QR Code")
    awb_income_ids = fields.One2many('income.2307','awb_2307','Income Payments')
    awb_money_ids = fields.One2many('money.2307','awb_money_2307','Money Payments')
    awb_payee_issue_date = fields.Date("Payee Date of Issue")
    awb_payee_expiry_date = fields.Date("Payee Date of Expiry")
    awb_payor_issue_date = fields.Date("Payor Date of Issue")
    awb_payor_expiry_date = fields.Date("Payor Date of Expiry")

    @api.onchange('awb_fiscal_year')
    def _onchange_fiscal_month(self):
        for rec in self:
            if rec.awb_fiscal_year:
                return {'domain': {
                    'awb_fiscal_quarter': [('awb_type', '=', 'quarterly'),('date_start', '>=', rec.awb_fiscal_year.date_from),('date_stop', '<=', rec.awb_fiscal_year.date_to)]}}
    
    @api.constrains('awb_payee_issue_date', 'awb_payee_expiry_date')
    def check_date(self):
        for rec in self:
            if rec.awb_payee_expiry_date < rec.awb_payee_issue_date:
                raise ValidationError('Payee Expiry Date must be grater than Payee Issue Date.')

    @api.constrains('awb_payor_issue_date', 'awb_payor_expiry_date')
    def check_date(self):
        for rec in self:
            if rec.awb_payor_expiry_date < rec.awb_payor_issue_date:
                raise ValidationError('Payor Expiry Date must be grater than Payor Issue Date.')

    # method is use to validate a state
    def action_validate(self):
        self.write({'awb_state': 'validated'})

    # method is use for set a state in Draft state
    def action_resetdraft(self):
        self.write({'awb_state': 'draft'})
        
    def action_report(self):
        return self.env.ref(
            'awb_philippine_tax_app.action_report_2307_report'
        ).report_action([])

    @api.onchange('awb_fiscal_quarter')
    def get_quarter_year(self):
        print("\n\n\n:::self.awb_fiscal_quarter.date_stop", self.awb_fiscal_quarter)
        if self.awb_fiscal_quarter:
            month = str(self.awb_fiscal_quarter.date_stop.strftime('%m/%d/%Y'))
            self.awb_month = month[0:2]
            self.awb_year = month[6:10]

    @api.depends('awb_entry_count')
    def check_journal_entry(self):
        if self.awb_move_id:
            self.awb_entry_count = True
        else:
            self.awb_entry_count = False
        

    def create_tax_calculation(self):
        if self.awb_income_ids:
            self.awb_income_ids = [(5, 0, 0)]
        line_ids = []
        for qtr in range(3):
            total_untaxed1 = []
            if qtr == 0:
                qua1_start_date = self.awb_fiscal_quarter.date_start + relativedelta(months=0)
                next_month = qua1_start_date.replace(day=28) + timedelta(days=4)
                qua1_end_date = next_month - timedelta(days=next_month.day)
                line_obj = self.env['account.move.line'].search([
                    ('move_id.move_type','in',('in_invoice','in_refund','entry')),
                    ('awb_tds_tag','=', True),
                    ('move_id.invoice_date', '>=', qua1_start_date),
                    ('move_id.invoice_date', '<=', qua1_end_date)])
                tds1_line = []
                tax1_line = []
                for line in line_obj:
                    if line.move_id not in tds1_line:
                        tds1_line.append(line.move_id)
                    if line.tax_ids not in tax1_line:
                        tax1_line.append(line.tax_ids)
                for tds in tds1_line:
                    for td in tds.invoice_line_ids:
                        for tax in tax1_line:
                            if td.awb_tds_tax_ids.name == tax.name:
                                data = {
                                    'awb_atc': tax.name,
                                    'awb_tax_base': td.price_subtotal,
                                    'inv_date': td.move_id.invoice_date,
                                }
                                total_untaxed1.append(data)
                for tax in tax1_line:
                    vals = {
                        'awb_income_payment': tax.awb_tax_description,
                        'awb_act': tax.id,
                        'awb_1st_month': sum([rec['awb_tax_base'] for rec in total_untaxed1 if ((rec['awb_atc'] == tax.name) and (rec['inv_date'], '>=', qua1_start_date) and (rec['inv_date'], '<=', qua1_end_date))]),
                        'awb_total': '',
                        'awb_tax_withheld': '',
                        'awb_2307': self.id
                    }
                    line_ids.append(vals)
                    self.awb_income_ids.create(vals)
            total_untaxed = []
            if qtr == 1:
                qua_start_date = self.awb_fiscal_quarter.date_start + relativedelta(months=1)
                next_month = qua_start_date.replace(day=28) + timedelta(days=4)
                qua_end_date = next_month - timedelta(days=next_month.day)
                line_obj = self.env['account.move.line'].search([
                    ('move_id.move_type','in',('in_invoice','in_refund','entry')),
                    ('awb_tds_tag','=', True),
                    ('move_id.invoice_date', '>=', qua_start_date),
                    ('move_id.invoice_date', '<=', qua_end_date)])
                tds_line = []
                tax_line = []
                for line in line_obj:
                    if line.move_id not in tds_line:
                        tds_line.append(line.move_id)
                    if line.tax_ids not in tax_line:
                        tax_line.append(line.tax_ids)
                for tds in tds_line:
                    for td in tds.invoice_line_ids:
                        for tax in tax_line:
                            if td.awb_tds_tax_ids.name == tax.name:
                                data = {
                                    'awb_atc': tax.name,
                                    'awb_tax_base': td.price_subtotal,
                                    'inv_date': td.move_id.invoice_date,
                                }
                                if data not in total_untaxed:
                                    total_untaxed.append(data)
                # print(total_untaxed,'2=============ATC')
                awb_1st_month = 0
                for tax in tax_line:
                    vals = {
                        'awb_income_payment': tax.awb_tax_description,
                        'awb_act': tax.id,
                        'awb_1st_month': sum([rec['awb_tax_base'] for rec in total_untaxed1 if ((rec['awb_atc'] == tax.name) and (rec['inv_date'], '>=', qua1_start_date) and (rec['inv_date'], '<=', qua1_end_date))]),
                        'awb_2st_month': sum([rec['awb_tax_base'] for rec in total_untaxed if ((rec['awb_atc'] == tax.name) and (rec['inv_date'], '>=', qua_start_date) and (rec['inv_date'], '<=', qua_end_date))]),
                        'awb_3st_month': sum([rec['awb_tax_base'] for rec in total_untaxed2 if ((rec['awb_atc'] == tax.name) and (rec['inv_date'], '>=', qua2_start_date) and (rec['inv_date'], '<=', qua2_end_date))]),
                        'awb_total': '',
                        'awb_tax_withheld': '', 
                        'awb_2307': self.id
                    }
                    line_ids.append(vals)
                    self.awb_income_ids.create(vals)

            total_untaxed2 = []
            if qtr == 2:
                qua2_start_date = self.awb_fiscal_quarter.date_start + relativedelta(months=2)
                next_month = qua2_start_date.replace(day=28) + timedelta(days=4)
                qua2_end_date = next_month - timedelta(days=next_month.day)
                line_obj = self.env['account.move.line'].search([
                    ('move_id.move_type','in',('in_invoice','in_refund','entry')),
                    ('awb_tds_tag','=', True),
                    ('move_id.invoice_date', '>=', qua2_start_date),
                    ('move_id.invoice_date', '<=', qua2_end_date)])
                tds2_line = []
                tax2_line = []
                for line in line_obj:
                    if line.move_id not in tds2_line:
                        tds2_line.append(line.move_id)
                    if line.tax_ids not in tax2_line:
                        tax2_line.append(line.tax_ids)
                for tds in tds2_line:
                    for td in tds.invoice_line_ids:
                        for tax in tax2_line:
                            if td.awb_tds_tax_ids.name == tax.name:
                                data = {
                                    'awb_atc': tax.name,
                                    'awb_tax_base': td.price_subtotal,
                                    'inv_date': td.move_id.invoice_date,
                                }
                                if data not in total_untaxed:
                                    total_untaxed2.append(data)
                # print(total_untaxed2,'3=============ATC')
                for tax in tax2_line:
                    vals = {
                        'awb_income_payment': tax.awb_tax_description,
                        'awb_act': tax.id,
                        'awb_1st_month': sum([rec['awb_tax_base'] for rec in total_untaxed1 if ((rec['awb_atc'] == tax.name) and (rec['inv_date'], '>=', qua1_start_date) and (rec['inv_date'], '<=', qua1_end_date))]),
                        'awb_2st_month': sum([rec['awb_tax_base'] for rec in total_untaxed if ((rec['awb_atc'] == tax.name) and (rec['inv_date'], '>=', qua_start_date) and (rec['inv_date'], '<=', qua_end_date))]),
                        'awb_3st_month': sum([rec['awb_tax_base'] for rec in total_untaxed2 if ((rec['awb_atc'] == tax.name) and (rec['inv_date'], '>=', qua2_start_date) and (rec['inv_date'], '<=', qua2_end_date))]),
                        'awb_total': '',
                        'awb_tax_withheld': '',
                        'awb_2307': self.id
                    }
                    line_ids.append(vals)
                    self.awb_income_ids.create(vals)
        # tax_line_data = {}
        # dic = {'awb_act': False, 'awb_1st_month': 0, 'awb_2st_month': 0, 'awb_3st_month': 0, 'awb_2307': False}
        # for rec in line_ids:
        #     tax_line_data.setdefault(tax.id, dic)
        #     tax_line_data[tax.id]['awb_atc'] = tax.id
        #     # tax_line_data[tax.id]['awb_1st_month'] =
        #     for key, value in tax_line_data.items():
        #         print(key,value,'===============line_ids',tax_line_data)
        #         # sale_obj.create(value) 

    def unlink(self):
        for res in self:
            if res.awb_state != 'draft':
                raise UserError('You are allowed to delete only in Draft!')
        return super(E2307, self).unlink()

    def generate_journal_Entry(self):
        partner = self.awb_partner_id
        journal = self.awb_journal_id
        output_19b = self.awb_19_b
        input_24 = self.awb_24
        output_account = self.env['account.account'].search([
            ('code', '=', 'Y'),
            ('name', '=', 'Output VAT')
        ])
        input_account = self.env['account.account'].search([
            ('code', '=', 'X'),
            ('name', '=', 'Input VAT')
        ])
        if output_account and input_account:
            line_values_debit = {'account_id': output_account.id,
                                 'partner_id': partner.id or False,
                                 }
            line_values_credit = {
                'account_id': input_account.id,
                'partner_id': partner.id or False,
            }
            line_values_payble = {
                'account_id': 17,
                'partner_id': partner.id,
            }
            if output_19b < input_24:
                line_values_debit.update({'debit': output_19b})
                line_values_credit.update({'credit': input_24})
                line_values_payble.update({'debit': input_24 - output_19b})
            elif output_19b > input_24:
                line_values_debit.update({'debit': output_19b})
                line_values_credit.update({'credit': input_24})
                line_values_payble.update({'credit': output_19b - input_24})
            else:
                pass
            line = {
                'type': 'entry',
                'company_id': self.awb_company_id.id,
                'journal_id': journal.id,
                'line_ids': [
                    (0, 0, line_values_credit),
                    (0, 0, line_values_debit),
                    (0, 0, line_values_payble)
                ]
            }
            move_id = self.env['account.move'].create(line)
            if move_id:
                self.write({
                    'awb_move_id': move_id.id,
                })

    def action_view_journal_entry_2550q(self):
        context = dict(self._context or {})
        # wiz_form_id = self.env['ir.model.data'].get_object_reference(
        #     'account', 'view_move_form')[1]
        if self.awb_move_id:
            return {
                'view_type': 'form',
                # 'view_id': wiz_form_id,
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.awb_move_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': context,
            }


class Income2307(models.Model):
    _name = "income.2307"

    awb_income_payment = fields.Char("Income Payments Subject to Expanded Withholding Tax")
    awb_act = fields.Many2one('account.tax', "ATC")
    awb_1st_month = fields.Float("1st Month of the Quarter")
    awb_2st_month = fields.Float("2st Month of the Quarter")
    awb_3st_month = fields.Float("3st Month of the Quarter")
    awb_total = fields.Float("Total", compute='_compute_total')
    awb_tax_withheld = fields.Float("Tax Withheld for the Quarter", compute='_compute_total')
    awb_2307 = fields.Many2one('e.2307')

    @api.depends('awb_1st_month','awb_2st_month','awb_3st_month')
    def _compute_total(self):
        for line in self:
            line.awb_total = line.awb_1st_month + line.awb_2st_month + line.awb_3st_month
            line.awb_tax_withheld = line.awb_act.amount * line.awb_total

class Money2307(models.Model):
    _name = "money.2307"

    awb_money_payment = fields.Char("Money Payments Subject to Expanded Withholding Tax")
    awb_act = fields.Many2one('account.tax', "ACT")
    awb_1st_month = fields.Float("1st Month of the Quarter")
    awb_2st_month = fields.Float("2st Month of the Quarter")
    awb_3st_month = fields.Float("3st Month of the Quarter")
    awb_total = fields.Float("Total")
    awb_tax_withheld = fields.Float("Tax Withheld for the Quarter")
    awb_money_2307 = fields.Many2one('e.2307')