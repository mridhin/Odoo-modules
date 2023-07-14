# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import datetime as dt
import datetime
import calendar


class E0619(models.Model):
    _name = "e.0619"
    _description = "0619E"
    _rec_name = 'awb_company_id'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    awb_company_id = fields.Many2one('res.company', string='Company')
    awb_partner_id = fields.Many2one('res.partner', string='Partner')
    awb_journal_id = fields.Many2one('account.journal', string='Journal')
    awb_fiscal_year = fields.Many2one(
        'account.fiscal.year', string='Fiscal Year')
    awb_month = fields.Char('Month')
    awb_year = fields.Char('Year')
    awb_entry_count = fields.Boolean(
        'Entry Count', default=False, compute='check_journal_entry')
    awb_move_id = fields.Many2one('account.move',
                                  string='Journal Entry',
                                  )
    awb_amended_return = fields.Selection(
        [('t', 'Yes'), ('f', 'No')], 'Amended Form?', default='f')
    awb_short_period_return = fields.Selection(
        [('tru', 'Yes'), ('fal', 'No')], 'Short Period Return', default='tru')
    awb_no_of_Sheets = fields.Integer('Sheets Attached')
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
    awb_atc = fields.Many2one('account.tax',string="ATC")
    awb_tax_type_code = fields.Char('TAX Type Code')
    awb_remittance = fields.Float('Amount of Remittance')
    awb_less_remittance = fields.Float('Less: Amount Remittance')
    awb_17a = fields.Float('17A')
    awb_17b = fields.Float('17B')
    awb_17c = fields.Float('17C')
    awb_17d = fields.Float('17D', compute='_compute_17d')
    awb_any_taxes_withheld = fields.Selection(
        [('t', 'Yes'), ('f', 'No')], 'Any Taxes Withheld?')
    awb_barcode = fields.Char("QR Code")
    awb_category_of_withholding_agent = fields.Selection(
        [('private', 'Private'), ('government', 'Government')], 'Category of Withholding Agent')
    awb_net_remittance = fields.Float("Net Amount of Remittance")
    awb_total_remittance = fields.Float("Total Amount of Remittance",compute='_compute_17d_remittance')
    awb_fiscal_quarter = fields.Many2one(
        'account.month.period', string='Fiscal Quarter')
    awb_fiscal_month = fields.Many2one(
        'account.month.period', string='Fiscal Month')
    awb_due_date = fields.Date('Due Date')
    awb_issue_date = fields.Date("Date of Issue")
    awb_expiry_date = fields.Date("Date of Expiry")

    @api.onchange('awb_fiscal_year')
    def _onchange_fiscal_month(self):
        for rec in self:
            if rec.awb_fiscal_year:
                return {'domain': {
                    'awb_fiscal_month': [('awb_type', '=', 'monthly'),('date_start', '>=', rec.awb_fiscal_year.date_from),('date_stop', '<=', rec.awb_fiscal_year.date_to)]}}

    @api.constrains('awb_issue_date', 'awb_expiry_date')
    def check_date(self):
        for rec in self:
            if rec.awb_expiry_date < rec.awb_issue_date:
                raise ValidationError('Date of Expiry must be grater than Date of Issue.')

    @api.constrains('awb_fiscal_month')
    def check_month(self):
        for rec in self:
            all_qtr = self.env['account.month.period'].search([('awb_type', '=', 'quarterly')])
            for qtr in all_qtr:
                qua_start_date = qtr.date_start + relativedelta(months=2)
                if rec.awb_fiscal_month.date_start == qua_start_date:
                    raise ValidationError('You can not create 0619-E report for March, June, September & December.')
                elif rec.awb_expiry_date < rec.awb_issue_date:
                    raise ValidationError('Date of Expiry date must be grater than Date of Issue.')

    @api.depends('awb_17d','awb_net_remittance')
    def _compute_17d_remittance(self):
        if self.awb_17d or self.awb_net_remittance:
            self.awb_total_remittance = self.awb_17d + self.awb_net_remittance
        else:
            self.awb_total_remittance = 0

    @api.depends('awb_17a','awb_17b','awb_17c')
    def _compute_17d(self):
        if self.awb_17a or self.awb_17b or self.awb_17c:
            self.awb_17d = self.awb_17a + self.awb_17b + self.awb_17c
        else:
            self.awb_17d = 0

    # @api.onchange('awb_fiscal_quarter')
    # def onchange_due_date(self):
    #     if self.awb_fiscal_quarter:
    #         date_after_month = self.awb_fiscal_quarter.date_stop + relativedelta(months=1)
    #         self.awb_due_date = date_after_month.strftime('%Y-%m-10')
    #     else:
    #         self.awb_due_date = ''

    # method is use to validate a state
    def action_validate(self):
        self.write({'awb_state': 'validated'})

    # method is use for set a state in Draft state
    def action_resetdraft(self):
        self.write({'awb_state': 'draft'})
        
    def action_report(self):
        return self.env.ref(
            'awb_philippine_tax_app.action_report_e_0619_report'
        ).report_action([])

    @api.onchange('awb_fiscal_month')
    def get_quarter_year(self):
        print("\n\n\n:::self.awb_fiscal_month.date_stop", self.awb_fiscal_month)
        if self.awb_fiscal_month:
            month = str(self.awb_fiscal_month.date_stop.strftime('%m/%d/%Y'))
            self.awb_month = month[0:2]
            self.awb_year = month[6:10]

    @api.depends('awb_entry_count')
    def check_journal_entry(self):
        if self.awb_move_id:
            self.awb_entry_count = True
        else:
            self.awb_entry_count = False

    def unlink(self):
        for res in self:
            if res.awb_state != 'draft':
                raise UserError('You are allowed to delete only in Draft!')
        return super(E0619, self).unlink()


    def action_generate_report_values(self):
        inv_domain = [
            ('invoice_date', '>=', self.awb_fiscal_month.date_start),
            ('invoice_date', '<=', self.awb_fiscal_month.date_stop),
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
        ]
        credit_domain = [
            ('invoice_date', '>=', self.awb_fiscal_month.date_start),
            ('invoice_date', '<=', self.awb_fiscal_month.date_stop),
            ('move_type', '=', 'in_refund'),
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
            self.awb_remittance = total_inv - total_credit
            self.awb_less_remittance = 0
            self.awb_net_remittance = self.awb_remittance
        elif self.awb_amended_return == 't':
            old_rec_id = self.env['e.0619'].search([('awb_amended_return','=','f')],limit=1)
            self.awb_remittance = total_inv - total_credit
            self.awb_less_remittance = old_rec_id.awb_remittance 
            self.awb_net_remittance = self.awb_remittance - self.awb_less_remittance

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
        old_rec_id = self.env['e.0619'].search([
            ('awb_amended_return','=', 'f'),
            ('awb_state','=','validated'),
            ('awb_fiscal_month','=', self.awb_fiscal_month.id),
        ],limit=1)
        if len(old_rec_id) > 0 and self.awb_amended_return == 'f':
            raise ValidationError(_('You have already generated Amended Form No for the same Fiscal Month.'))
