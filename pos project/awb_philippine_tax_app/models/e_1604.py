# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import datetime
import calendar


period_list = [
        ('Q1', '1st Quarter'),
        ('Q2', '2st Quarter'),
        ('Q3', '3st Quarter'),
        ('Q4', '4st Quarter'),
    ]

month_list = [
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]


class E1604(models.Model):
    _name = "e.1604"
    _description = "1604-E"
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
    # Visible or invisible fields
    awb_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('amendment', 'Amendment')], tracking=True,
        required=True, readonly=True, default='draft', copy=False)
    awb_barcode = fields.Char("QR Code")
    awb_schedule1_ids = fields.One2many('schedule1.1604','awb_1604','Schedule1')
    awb_schedule2_ids = fields.One2many('schedule2.1604','awb_1604','Schedule2')
    awb_count_schedule = fields.Boolean("Count Schedule")
    awb_remittance_date = fields.Date("Date of Remittance")
    awb_issue_date = fields.Date("Date of Issue")
    awb_expiry_date = fields.Date("Date of Expiry")

    @api.onchange('awb_fiscal_year')
    def _onchange_fiscal_month(self):
        for rec in self:
            if rec.awb_fiscal_year:
                return {'domain': {
                    'awb_fiscal_quarter': [('awb_type', '=', 'quarterly'),('date_start', '>=', rec.awb_fiscal_year.date_from),('date_stop', '<=', rec.awb_fiscal_year.date_to)]}}
    
    def create_schedule(self):
        eq_line_ids = self.env['eq.1601'].search([('awb_state','=','validated')])
        for rec in self:
            if rec.awb_schedule1_ids and rec.awb_schedule2_ids:
                rec.awb_schedule1_ids = [(5, 0, 0)]
                rec.awb_schedule2_ids = [(5, 0, 0)]
            for period in period_list:
                schedule1 = {
                    'awb_quarter': period[1],
                    # 'awb_date_of_remittance': '',
                    # 'awb_drawee': '',
                    # 'awb_tra_no': '',
                    'awb_taxes_withheld': sum([line.awb_total_remittance for line in eq_line_ids if (period[0] == line.awb_fiscal_quarter.code.split("/", 1)[0]) and (rec.awb_fiscal_year.name == line.awb_fiscal_year.name)]),
                    'awb_penalties': sum([line.awb_total_penalties for line in eq_line_ids if (period[0] == line.awb_fiscal_quarter.code.split("/", 1)[0]) and (rec.awb_fiscal_year.name == line.awb_fiscal_year.name)]),
                    'awb_amount_remitted': sum([line.awb_total_due for line in eq_line_ids if (period[0] == line.awb_fiscal_quarter.code.split("/", 1)[0]) and (rec.awb_fiscal_year.name == line.awb_fiscal_year.name)]),
                    'awb_1604': rec.id
                }
                rec.awb_schedule1_ids.create(schedule1)
            for month in month_list:
                schedule2 = {
                    'awb_months': month[1],
                    # 'awb_date_of_remittance': '',
                    # 'awb_drawee': '',
                    # 'awb_tra_no': '',
                    # 'awb_taxes_withheld': '',
                    # 'awb_penalties': '',
                    # 'awb_amount_remitted': '',
                    'awb_1604': rec.id
                }
                rec.awb_schedule2_ids.create(schedule2)
            rec.awb_count_schedule = True


    # method is use to validate a state
    def action_validate(self):
        self.write({'awb_state': 'validated'})

    # method is use for set a state in Draft state
    def action_resetdraft(self):
        self.write({'awb_state': 'draft'})
        
    def action_report(self):
        return self.env.ref(
            'awb_philippine_tax_app.action_report_e_1604_report'
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
        # if not data_list:
        # raise UserError(_('No records found'))
        # else:
        return self.env.ref(
            'awb_philippine_tax_app.action_report_q_2550_report'
        ).report_action([])

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

    def unlink(self):
        for res in self:
            if res.awb_state != 'draft':
                raise UserError('You are allowed to delete only in Draft!')
        return super(E1604, self).unlink()

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

class E1604Schdule1(models.Model):
    _name = "schedule1.1604"

    awb_quarter = fields.Char("Quarters")
    awb_date_of_remittance = fields.Date("Date of Remittance")
    awb_drawee = fields.Char("Drawee Bank/Bank Code/Agency")
    awb_tra_no = fields.Char("TRA/eROR/eAR Number")
    awb_taxes_withheld = fields.Float("Taxes Withheld")#, compute='compute_tax_withheld')
    awb_penalties = fields.Float("Penalties")
    awb_amount_remitted = fields.Float("Total Amount Remitted")
    awb_1604 = fields.Many2one('e.1604')


    # @api.depends('awb_quarter')
    # def compute_tax_withheld(self):
    #     for rec in self:
    #     # for period in period_list:
    #         rec_id = self.env['eq.1601'].search([('awb_state','=','validated')])
    #         val = 0
    #         # for rec_id in eq_ids:
    #         if rec_id.awb_quater == 'Q1':
    #             print(rec_id.awb_quater,'1============period[1]',rec_id)
    #             val = rec_id.awb_total_remittance
    #             rec.awb_taxes_withheld = val
            # elif rec_id.awb_quater == 'Q2':
            #     print(period[1],'2============period[1]',rec_id)
            #     val = rec_id.awb_total_remittance
            #     self.awb_taxes_withheld = val
            # elif rec_id.awb_quater == 'Q3':
            #     print(period[1],'3============period[1]',rec_id)
            #     val = rec_id.awb_total_remittance
            #     self.awb_taxes_withheld = val
            # elif rec_id.awb_quater == 'Q4':
            #     print(period[1],'4============period[1]',rec_id)
            #     val = rec_id.awb_total_remittance
            #     self.awb_taxes_withheld = val

                        # schedule1 = {
                        #     'awb_quarter': period[1],
                        #     # 'awb_date_of_remittance': '',
                        #     # 'awb_drawee': '',
                        #     # 'awb_tra_no': '',
                        #     'awb_taxes_withheld': val,
                        #     # 'awb_penalties': '',
                        #     # 'awb_amount_remitted': '',
                        #     'awb_1604': rec.id
                        # }
                        # rec.awb_schedule1_ids.update(schedule1)
            


class E1604Schdule2(models.Model):
    _name = "schedule2.1604"

    awb_months = fields.Char("Months")
    awb_date_of_remittance = fields.Date("Date of Remittance")
    awb_drawee = fields.Char("Drawee Bank/Bank Code/Agency")
    awb_tra_no = fields.Char("TRA/eROR/eAR Number")
    awb_taxes_withheld = fields.Float("Taxes Withheld")
    awb_penalties = fields.Float("Penalties")
    awb_amount_remitted = fields.Float("Total Amount Remitted")
    awb_1604 = fields.Many2one('e.1604')