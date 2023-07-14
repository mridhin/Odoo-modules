# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import datetime
import calendar

atc_list = [
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
]

class EQ1601(models.Model):
    _name = "eq.1601"
    _description = "1601-EQ"
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
    awb_move_id = fields.Many2one('account.move', string='Journal Entry',)
    awb_amended_return = fields.Selection(
        [('t', 'Yes'), ('f', 'No')], 'Amended Return?', default='f')
    awb_short_period_return = fields.Selection(
        [('tru', 'Yes'), ('fal', 'No')], 'Short Period Return', default='tru')
    awb_no_of_Sheets = fields.Integer('No. of Sheets Attached')
    awb_special_tax_or_inter_tax_treaty = fields.Selection(
        [('y', 'Yes'), ('n', 'No')],
        string='tax relief under Special Law or International Tax Treaty', default='n')
    awb_specify = fields.Char('If Yes, please specify')
    # Visible or invisible fields
    awb_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('amendment', 'Amendment')], tracking=True,
        required=True, readonly=True, default='draft', copy=False)
    awb_any_taxes_withheld = fields.Selection(
        [('t', 'Yes'), ('f', 'No')], 'Any Taxes Withheld?')
    awb_category_of_withholding_agent = fields.Selection(
        [('private', 'Private'), ('government', 'Government')], 'Category of Withholding Agent')
    awb_tax_code = fields.Selection(
        [('wc158', 'WC158'), 
        ('wc100', 'WC100'),
        ('wi160', 'WI160')], 'ATC Tax Code')
    awb_surcharge = fields.Float('Surcharge')
    awb_interest = fields.Float('Interest')
    awb_compromise = fields.Float('Compromise')
    awb_if_over_remittance = fields.Selection(
        [('to_be_refunded', 'To be refunded'), 
        ('to_be_issued_tax', 'To be issued Tax Credit Certificate'),
        ('to_be_carried_over', 'To be carried over')], 'If Over-Remittance?')
    awb_is_quater = fields.Boolean('Is Quarter?')
    awb_quater = fields.Char(compute='_compute_quater', store=True)
    awb_barcode = fields.Char("QR Code")
    awb_category_of_withholding_agent = fields.Selection(
        [('private', 'Private'), ('government', 'Government')], 'Category of Withholding Agent')
    awb_23 = fields.Float("Over-remittance from Previous Quarter")
    awb_24 = fields.Float("Other Payments Made")
    awb_eq_line_ids = fields.One2many('eq_1601.line','awb_eq_1601','EQ-1601 Line')
    awb_total_amt = fields.Float("Total", compute='_compute_total')
    awb_1st_month_qtr = fields.Float("Remittances Made: 1st Month of the Quarter", compute='_compute_total_values')
    awb_2st_month_qtr = fields.Float("Remittances Made: 2st Month of the Quarter", compute='_compute_total_values')
    awb_tax_remittance = fields.Float("Tax Remitted in Return Previously Filed", compute='_compute_remittance')
    awb_total_remittance = fields.Float("Total Remittances Made" ,compute='_compute_total_remittance')
    awb_total_penalties = fields.Float("Total Penalties", compute='_compute_total_penalty')
    awb_tax_due = fields.Float("Tax Still Due", compute='_compute_tax_due')
    awb_total_due = fields.Float("Total Amount Still Due", compute='_compute_total_due')
    awb_issue_date = fields.Date("Date of Issue")
    awb_expiry_date = fields.Date("Date of Expiry")

    @api.onchange('awb_fiscal_year')
    def _onchange_fiscal_month(self):
        for rec in self:
            if rec.awb_fiscal_year:
                return {'domain': {
                    'awb_fiscal_quarter': [('awb_type', '=', 'quarterly'),('date_start', '>=', rec.awb_fiscal_year.date_from),('date_stop', '<=', rec.awb_fiscal_year.date_to)]}}

    @api.constrains('awb_issue_date', 'awb_expiry_date')
    def check_date(self):
        for rec in self:
            if rec.awb_expiry_date < rec.awb_issue_date:
                raise ValidationError('Expiry date must be grater than Issue date.')
    
    @api.depends('awb_total_amt','awb_total_remittance')
    def _compute_tax_due(self):
        for rec in self:
            rec.awb_tax_due = rec.awb_total_amt - rec.awb_total_remittance

    @api.depends('awb_tax_due','awb_total_penalties')
    def _compute_total_due(self):
        for rec in self:
            rec.awb_total_due = rec.awb_tax_due - rec.awb_total_penalties

    @api.depends('awb_surcharge','awb_interest','awb_compromise')
    def _compute_total_penalty(self):
        for rec in self:
            rec.awb_total_penalties = rec.awb_surcharge + rec.awb_interest + rec.awb_compromise

    @api.depends('awb_1st_month_qtr','awb_2st_month_qtr','awb_23','awb_24')
    def _compute_total_remittance(self):
        for rec in self:
            rec.awb_total_remittance = rec.awb_1st_month_qtr + rec.awb_2st_month_qtr + rec.awb_23 + rec.awb_24

    @api.depends('awb_fiscal_quarter')
    def _compute_remittance(self):
        inv_domain = [
            ('invoice_date', '>=', self.awb_fiscal_quarter.date_start),
            ('invoice_date', '<=', self.awb_fiscal_quarter.date_stop),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ]
        credit_domain = [
            ('invoice_date', '>=', self.awb_fiscal_quarter.date_start),
            ('invoice_date', '<=', self.awb_fiscal_quarter.date_stop),
            ('move_type', '=', 'out_refund'),
            ('state', '=', 'posted'),
        ]
        inv_obj = self.env['account.move'].search(inv_domain)
        credit_obj = self.env['account.move'].search(credit_domain)
        total_inv = 0
        total_credit = 0
        for move in inv_obj:
            for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids):
                total_inv += line.awb_ewt_total
        for move in credit_obj:
            for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids):
                total_credit += line.awb_ewt_total
        if self.awb_amended_return == 'f':
            self.awb_tax_remittance = total_inv - total_credit
        elif self.awb_amended_return == 't':
            old_rec_id = self.env['eq.1601'].search([('awb_amended_return','=','f')],limit=1)
            if old_rec_id:
                self.awb_tax_remittance = old_rec_id.awb_tax_remittance

    @api.depends('awb_total_amt')
    def _compute_total_values(self):
        month_one = self.env['e.0619'].search([('awb_amended_return','=','f'),('awb_state','=','validated')],limit=1)
        month_two = self.env['e.0619'].search([('awb_amended_return','=','t'),('awb_state','=','validated')],limit=1)
        if month_one or month_two:
            self.awb_1st_month_qtr = month_one.awb_remittance
            self.awb_2st_month_qtr = month_two.awb_remittance
        else:
            self.awb_1st_month_qtr = 0
            self.awb_2st_month_qtr = 0

    @api.depends('awb_eq_line_ids')
    def _compute_total(self):
        for rec in self:
            rec.awb_total_amt = sum([rec.awb_tax_withheld for rec in rec.awb_eq_line_ids])  

    def action_cal_tax(self):
        tds_line = []
        tax_line = []
        total_untaxed = []
        line_obj = self.env['account.move.line'].search([('move_id.move_type','in',('in_invoice','in_refund','entry')),('awb_tds_tag','=', True),('move_id.invoice_date', '>=', self.awb_fiscal_quarter.date_start),('move_id.invoice_date', '<=', self.awb_fiscal_quarter.date_stop)])
        for line in line_obj:
            if line.move_id not in tds_line:
                tds_line.append(line.move_id)
            if line.tax_ids not in tax_line:
                tax_line.append(line.tax_ids)
        if self.awb_eq_line_ids:
            self.awb_eq_line_ids = [(5, 0, 0)]
        for tds in tds_line:
            for td in tds.invoice_line_ids:
                for tax in tax_line:
                    if td.awb_tds_tax_ids.name == tax.name:
                        data = {
                            'awb_atc': tax.name,
                            'awb_tax_base': td.price_subtotal,
                        }
                        total_untaxed.append(data)
        print(total_untaxed,'=============ATC')
        for tax in tax_line:
            vals = {
                'awb_atc': tax.id,
                'awb_tax_base': sum([rec['awb_tax_base'] for rec in total_untaxed if rec['awb_atc'] == tax.name]),
                'awb_tax_rate': tax.amount,
                'awb_tax_withheld': '',
                'awb_eq_1601': self.id
            }
            self.awb_eq_line_ids.create(vals)

    @api.depends('awb_fiscal_quarter')
    def _compute_quater(self):
        if self.awb_fiscal_quarter:
            quarter = (self.awb_fiscal_quarter.code.split("/", 1)[0])
            self.awb_quater = quarter
        else:
            self.awb_quater = False

    # method is use to validate a state
    def action_validate(self):
        self.write({'awb_state': 'validated'})

    # method is use for set a state in Draft state
    def action_resetdraft(self):
        self.write({'awb_state': 'draft'})
        
    def action_report(self):
        return self.env.ref(
            'awb_philippine_tax_app.action_report_eq_1601_report'
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

    def action_report_2550q(self):
        # Method to M2550 report
        return self.env.ref(
            'awb_philippine_tax_app.action_report_q_2550_report'
        ).report_action([])        

    def unlink(self):
        for res in self:
            if res.awb_state != 'draft':
                raise UserError('You are allowed to delete only in Draft!')
        return super(EQ1601, self).unlink()

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
                'move_type': 'entry',
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

    @api.constrains('awb_amended_return')
    def count_0619_rec(self):
        old_rec_id = self.env['eq.1601'].search([
            ('awb_amended_return','=', 'f'),
            ('awb_state','=','validated'),
            ('awb_fiscal_quarter','=', self.awb_fiscal_quarter.id),
        ],limit=1)
        if len(old_rec_id) > 0 and self.awb_amended_return == 'f':
            raise ValidationError(_('You can not create another Amended Return No!'))


class EQ1601Line(models.Model):
    _name = "eq_1601.line"

    awb_atc = fields.Many2one('account.tax', string="ATC")
    awb_tax_base = fields.Float("Tax Base (Consolidated for the Quarter)")
    awb_tax_rate = fields.Float("Tax Rate")
    awb_tax_withheld = fields.Float("Tax Withheld (Consolidated for the Quarter)", compute='_compute_withhold')
    awb_eq_1601 = fields.Many2one('eq.1601')

    @api.depends('awb_tax_base', 'awb_tax_rate')
    def _compute_withhold(self):
        for rec in self:
            rec.awb_tax_withheld = rec.awb_tax_rate * rec.awb_tax_base

    # @api.onchange('awb_atc','awb_tax_base')
    # def _compute_atc(self):
    #     for rec in self:
    #         start_date = rec.awb_eq_1601.awb_fiscal_quarter.date_start
    #         end_date = rec.awb_eq_1601.awb_fiscal_quarter.date_stop
    #         domain = [
    #             ('invoice_date', '>=', start_date),
    #             ('invoice_date', '<=', end_date),
    #             ('state', '=', 'posted'),
    #             ('move_type', '=', 'out_invoice')
    #         ]
    #         move_obj = rec.env['account.move'].search(domain)
    #         wi555 = 0
    #         wi556 = 0
    #         wi557 = 0
    #         wi558 = 0
    #         wc555 = 0
    #         wc556 = 0
    #         wc557 = 0
    #         wc558 = 0
    #         for move in move_obj:
    #             total_wi555 = 0
    #             total_wi556 = 0
    #             total_wi557 = 0
    #             total_wi558 = 0
    #             total_wc555 = 0
    #             total_wc556 = 0
    #             total_wc557 = 0
    #             total_wc558 = 0
    #             if rec.awb_atc.name == 'WI555-PH' and rec.awb_atc:
    #                 total_wi555 = sum([line.price_subtotal for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WI555-PH'])
    #                 rec.awb_tax_rate = rec.awb_atc.amount
    #                 wi555 += total_wi555
    #             elif rec.awb_atc.name == 'WI556-PH' and rec.awb_atc:
    #                 total_wi556 = sum([line.price_subtotal for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WI556-PH'])
    #                 rec.awb_tax_rate = rec.awb_atc.amount
    #                 wi556 += total_wi556
    #             elif rec.awb_atc.name == 'WI557-PH':
    #                 total_wi557 = sum([line.price_subtotal for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WI557-PH'])
    #                 rec.awb_tax_rate = self.awb_atc.amount
    #                 wi557 += total_wi557
    #             elif self.awb_atc.name == 'WI558-PH':
    #                 total_wi558 = sum([line.move_id.amount_untaxed for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WI558-PH'])
    #                 rec.awb_tax_rate = self.awb_atc.amount
    #                 wi558 += total_wi558
    #             elif self.awb_atc.name == 'WC555-PH':
    #                 total_wc555 = sum([line.move_id.amount_untaxed for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WC555-PH'])
    #                 rec.awb_tax_rate = self.awb_atc.amount
    #                 wc555 += total_wc555
    #             elif self.awb_atc.name == 'WC556-PH':
    #                 total_wc556 = sum([line.move_id.amount_untaxed for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WC556-PH'])
    #                 rec.awb_tax_rate = self.awb_atc.amount
    #                 wc556 += total_wc556
    #             elif self.awb_atc.name == 'WC557-PH':
    #                 total_wc557 = sum([line.move_id.amount_untaxed for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WC557-PH'])
    #                 rec.awb_tax_rate = self.awb_atc.amount
    #                 wc557 += total_wc557
    #             elif self.awb_atc.name == 'WC558-PH':
    #                 total_wc558 = sum([line.move_id.amount_untaxed for line in move.invoice_line_ids.filtered(lambda x: x.awb_tds_tax_ids) if line.awb_tds_tax_ids.name == 'WC558-PH'])
    #                 rec.awb_tax_rate = self.awb_atc.amount
    #                 wc558 += total_wc558
    #             else:
    #                 rec.awb_tax_rate = 0
    #                 rec.awb_tax_base = 0
    #         print(wi555,"2===============atc",wi556, wi557)
    #         if rec.awb_atc.name == 'WI555-PH' and wi555:
    #             rec.awb_tax_base = wi555
    #         elif rec.awb_atc.name == 'WI556-PH' and wi556:
    #             rec.awb_tax_base = wi556
    #         elif rec.awb_atc.name == 'WI557-PH' and wi557:
    #             rec.awb_tax_base = wi557
    #         elif rec.awb_atc.name == 'WI558-PH' and wi558:
    #             rec.awb_tax_base = wi558
    #         elif rec.awb_atc.name == 'WC555-PH' and wc555:
    #             rec.awb_tax_base = wc555
    #         elif rec.awb_atc.name == 'WC556-PH' and wc556:
    #             rec.awb_tax_base = wc556
    #         elif rec.awb_atc.name == 'WC557-PH' and wc557:
    #             rec.awb_tax_base = wc557
    #         elif rec.awb_atc.name == 'WC558-PH' and wc558:
    #             rec.awb_tax_base = wc558
    #         else:
    #             rec.awb_tax_base = 0
                
                
                