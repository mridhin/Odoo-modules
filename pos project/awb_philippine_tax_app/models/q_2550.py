# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError


class Q2550(models.Model):
    _name = "q.2550"
    _description = "2550Q"
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
        [('t', 'Yes'), ('f', 'No')], 'Amended Return', default='f')
    awb_short_period_return = fields.Selection(
        [('tru', 'Yes'), ('fal', 'No')], 'Short Period Return', default='tru')
    awb_no_of_Sheets = fields.Integer('Sheets Attached')
    awb_special_tax_or_inter_tax_treaty = fields.Selection(
        [('y', 'Yes'), ('n', 'No')],
        string='tax relief under Special Law or International Tax Treaty', default='n')
    awb_specify = fields.Char('If Yes, please specify')
    # Visible or invisible fields
    awb_15_a = fields.Float('15A')
    awb_15_b = fields.Float('15B')
    awb_16_a = fields.Float('16A')
    awb_16_b = fields.Float('16B')
    awb_17 = fields.Float('17 Zero Rated Sales/Receipts')
    awb_18 = fields.Float('18 Exempt Sales/Receipts')
    awb_19_a = fields.Float('19A')
    awb_19_b = fields.Float('19B')
    awb_20_a = fields.Float('20A')
    awb_20_b = fields.Float('20B')
    awb_20_c = fields.Float('20C')
    awb_20_d = fields.Float('20D')
    awb_20_e = fields.Float('20E')
    awb_20_f = fields.Float('20F')
    awb_21_a = fields.Float('21A')
    awb_21_b = fields.Float('21B')
    awb_21_c = fields.Float('21C')
    awb_21_d = fields.Float('21D')
    awb_21_e = fields.Float('21E')
    awb_21_f = fields.Float('21F')
    awb_21_g = fields.Float('21G')
    awb_21_h = fields.Float('21H')
    awb_21_i = fields.Float('21I')
    awb_21_j = fields.Float('21J')
    awb_21_k = fields.Float('21K')
    awb_21_l = fields.Float('21L')
    awb_21_m = fields.Float('21M')
    awb_21_n = fields.Float('21N')
    awb_21_0 = fields.Float('210')
    awb_21_p = fields.Float('21P')
    awb_22 = fields.Float('22')
    awb_23_a = fields.Float('23A')
    awb_23_b = fields.Float('23B')
    awb_23_c = fields.Float('23C')
    awb_23_d = fields.Float('23D')
    awb_23_e = fields.Float('23E')
    awb_23_f = fields.Float('23F')
    awb_24 = fields.Float('24')
    awb_25 = fields.Float('25')
    awb_26_a = fields.Float('26A')
    awb_26_b = fields.Float('26B')
    awb_26_c = fields.Float('26C')
    awb_26_d = fields.Float('26D')
    awb_26_e = fields.Float('26E')
    awb_26_f = fields.Float('26F')
    awb_26_g = fields.Float('26G')
    awb_26_h = fields.Float('26H')
    awb_27 = fields.Float('27')
    awb_28_a = fields.Float('28A')
    awb_28_b = fields.Float('28B')
    awb_28_c = fields.Float('28C')
    awb_28_d = fields.Float('28D')
    awb_29 = fields.Float('29')
    awb_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('amendment', 'Amendment')], tracking=True,
        required=True, readonly=True, default='draft', copy=False)

    # method is use to validate a state
    def action_validate(self):
        self.write({'awb_state': 'validated'})

    # method is use for set a state in Draft state
    def action_resetdraft_2550q(self):
        self.write({'awb_state': 'draft'})

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

    def action_generate_report_values(self):
        self._quarterly_count_sale_ammount_tax_count()
        self._quarterly_count_purchase_ammount_tax_count()
        self._calculation_wizard_field()

    def _quarterly_count_sale_ammount_tax_count(self):
        main_obj = self
        start_date = main_obj.awb_fiscal_quarter.date_start
        end_date = main_obj.awb_fiscal_quarter.date_stop
        company = main_obj.awb_company_id
        domain = [
            ('move_id.invoice_date', '>=', start_date),
            ('move_id.invoice_date', '<=', end_date),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', company.id)
        ]
        move_line_obj = main_obj.env['account.move.line'].search(domain)
        sale_untax_amt_sph = 0
        sale_tax_amt_sph = 0
        sale_untax_amt_gph = 0
        sale_tax_amt_gph = 0
        sale_untax_amt_zph = 0
        sale_untax_amt_exph = 0
        for move_line in move_line_obj:
            if move_line.move_id.move_type in ['out_invoice', 'out_receipt']:
                if move_line.tax_ids.name in ['EX-PH', 'Z-PH', 'G-PH', 'S-PH'] and move_line.tax_ids.type_tax_use == 'sale':
                    if move_line.tax_ids.name == 'EX-PH':
                        sale_untax_amt_exph = \
                            sale_untax_amt_exph + move_line.price_subtotal
                    if move_line.tax_ids.name == 'Z-PH':
                        sale_untax_amt_zph = sale_untax_amt_zph + move_line.price_subtotal
                    if move_line.tax_ids.name == 'G-PH':
                        sale_tax_amt_gph = sale_tax_amt_gph + move_line.price_total
                        sale_untax_amt_gph = sale_untax_amt_gph + move_line.price_subtotal
                    if move_line.tax_ids.name == 'S-PH':
                        sale_tax_amt_sph = sale_tax_amt_sph + move_line.price_total
                        sale_untax_amt_sph = sale_untax_amt_sph + move_line.price_subtotal
            elif move_line.move_id.move_type in ['out_refund']:
                if move_line.tax_ids.name in ['EX-PH', 'Z-PH', 'G-PH', 'S-PH']:
                    if move_line.tax_ids.name == 'EX-PH':
                        sale_untax_amt_exph = sale_untax_amt_exph - move_line.price_subtotal
                    if move_line.tax_ids.name == 'Z-PH':
                        sale_untax_amt_zph = sale_untax_amt_zph - move_line.price_subtotal
                    if move_line.tax_ids.name == 'G-PH':
                        sale_tax_amt_gph = sale_tax_amt_gph - move_line.price_total
                        sale_untax_amt_gph = sale_untax_amt_gph - move_line.price_subtotal
                    if move_line.tax_ids.name == 'S-PH':
                        sale_tax_amt_sph = sale_tax_amt_sph - move_line.price_total
                        sale_untax_amt_sph = sale_untax_amt_sph - move_line.price_subtotal
            else:
                pass
        print(sale_untax_amt_exph,'================domain',move_line_obj)
        # print(HH)
        main_obj.awb_15_a = sale_untax_amt_sph
        main_obj.awb_15_b = sale_tax_amt_sph - main_obj.awb_15_a
        main_obj.awb_16_a = sale_untax_amt_gph 
        main_obj.awb_16_b = sale_tax_amt_gph - main_obj.awb_16_a
        main_obj.awb_17 = sale_untax_amt_zph
        main_obj.awb_18 = sale_untax_amt_exph
        main_obj.awb_19_a = main_obj.awb_15_a + \
            main_obj.awb_16_a + main_obj.awb_17 + main_obj.awb_18
        main_obj.awb_19_b = main_obj.awb_15_b + main_obj.awb_16_a

    def _quarterly_count_purchase_ammount_tax_count(self):
        main_obj = self
        start_date = main_obj.awb_fiscal_quarter.date_start
        end_date = main_obj.awb_fiscal_quarter.date_stop
        company = main_obj.awb_company_id
        domain = [
            ('move_id.invoice_date', '>=', start_date),
            ('move_id.invoice_date', '<=', end_date),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', company.id),
            ('move_id.move_type', 'in', ['in_invoice', 'in_receipt', 'in_refund'])
        ]
        move_line_obj = main_obj.env['account.move.line'].search(domain)
        purchase_untax_amt_capph_moreless1m = 0
        purchase_tax_amt_capph_moreless1m = 0
        purchase_untax_amt_sph = 0
        purchase_tax_amt_sph = 0
        purchase_untax_amt_imptph = 0
        purchase_tax_amt_imptph = 0
        purchase_untax_amt_svcph = 0
        purchase_tax_amt_svcph = 0
        purchase_untax_amt_svcaph = 0
        purchase_tax_amt_svcaph = 0
        purchase_untax_amt_exph = 0
        purchase_untax_amt_zph = 0
        for move_line in move_line_obj:
            if move_line.move_id.move_type in ['in_invoice', 'in_receipt']:
                if move_line.tax_ids.name in\
                    ['IMPT-PH', 'SVCA-PH', 'S-PH', 'SVC-PH', 'CAP-PH', 'EX-PH', 'Z-PH'] \
                        and move_line.tax_ids.type_tax_use == 'purchase':
                    if move_line.tax_ids.name == 'CAP-PH':
                        purchase_untax_amt_capph_moreless1m = \
                            purchase_untax_amt_capph_moreless1m + move_line.price_subtotal
                        purchase_tax_amt_capph_moreless1m = \
                            purchase_tax_amt_capph_moreless1m + move_line.price_total
                    if move_line.tax_ids.name == 'S-PH':
                        purchase_untax_amt_sph = \
                            purchase_untax_amt_sph + move_line.price_subtotal
                        purchase_tax_amt_sph = \
                            purchase_tax_amt_sph + move_line.price_total
                    if move_line.tax_ids.name == 'IMPT-PH':
                        purchase_untax_amt_imptph = \
                            purchase_untax_amt_imptph + move_line.price_subtotal
                        purchase_tax_amt_imptph = \
                            purchase_tax_amt_imptph + move_line.price_total
                    if move_line.tax_ids.name == 'SVC-PH':
                        purchase_untax_amt_svcph = \
                            purchase_untax_amt_svcph + move_line.price_subtotal
                        purchase_tax_amt_svcph = \
                            purchase_tax_amt_svcph + move_line.price_total
                    if move_line.tax_ids.name == 'SVCA-PH':
                        purchase_untax_amt_svcaph = \
                            purchase_untax_amt_svcaph + move_line.price_subtotal
                        purchase_tax_amt_svcaph = \
                            purchase_tax_amt_svcaph + move_line.price_total
                    if move_line.tax_ids.name == 'EX-PH':
                        purchase_untax_amt_exph = \
                            purchase_untax_amt_exph + move_line.price_subtotal
                    if move_line.tax_ids.name == 'Z-PH':
                        purchase_untax_amt_zph = \
                            purchase_untax_amt_zph + move_line.price_subtotal

            elif move_line.move_id.move_type in ['in_refund']:
                if move_line.tax_ids.name in\
                    ['IMPT-PH', 'SVCA-PH', 'S-PH', 'SVC-PH', 'CAP-PH', 'EX-PH', 'Z-PH'] \
                        and move_line.tax_ids.type_tax_use == 'purchase':
                    if move_line.tax_ids.name == 'CAP-PH':
                        purchase_untax_amt_capph_moreless1m = \
                            purchase_untax_amt_capph_moreless1m - move_line.price_subtotal
                        purchase_tax_amt_capph_moreless1m = \
                            purchase_tax_amt_capph_moreless1m - move_line.price_total
                    if move_line.tax_ids.name == 'S-PH':
                        purchase_untax_amt_sph = \
                            purchase_untax_amt_sph - move_line.price_subtotal
                        purchase_tax_amt_sph = \
                            purchase_tax_amt_sph - move_line.price_total
                    if move_line.tax_ids.name == 'IMPT-PH':
                        purchase_untax_amt_imptph = \
                            purchase_untax_amt_imptph - move_line.price_subtotal
                        purchase_tax_amt_imptph = \
                            purchase_tax_amt_imptph - move_line.price_total
                    if move_line.tax_ids.name == 'SVC-PH':
                        purchase_untax_amt_svcph = \
                            purchase_untax_amt_svcph - move_line.price_subtotal
                        purchase_tax_amt_svcph = \
                            purchase_tax_amt_svcph - move_line.price_total
                    if move_line.tax_ids.name == 'SVCA-PH':
                        purchase_untax_amt_svcaph = \
                            purchase_untax_amt_svcaph - move_line.price_subtotal
                        purchase_tax_amt_svcaph = \
                            purchase_tax_amt_svcaph - move_line.price_total
                    if move_line.tax_ids.name == 'EX-PH':
                        purchase_untax_amt_exph = \
                            purchase_untax_amt_exph - move_line.price_subtotal
                    if move_line.tax_ids.name == 'Z-PH':
                        purchase_untax_amt_zph = \
                            purchase_untax_amt_zph - move_line.price_subtotal
            if purchase_untax_amt_capph_moreless1m < 1000000:
                main_obj.awb_21_a = purchase_untax_amt_capph_moreless1m
            if purchase_untax_amt_capph_moreless1m >= 1000000:
                main_obj.awb_21_c = purchase_untax_amt_capph_moreless1m
            if purchase_tax_amt_capph_moreless1m < 1000000:
                main_obj.awb_21_b = purchase_tax_amt_capph_moreless1m - main_obj.awb_21_a
            if purchase_tax_amt_capph_moreless1m >= 1000000:
                main_obj.awb_21_d = purchase_tax_amt_capph_moreless1m - main_obj.awb_21_c
            main_obj.awb_21_e = purchase_untax_amt_sph
            main_obj.awb_21_f = purchase_tax_amt_sph - main_obj.awb_21_e
            main_obj.awb_21_g = purchase_untax_amt_imptph
            main_obj.awb_21_h = purchase_tax_amt_imptph - main_obj.awb_21_g
            main_obj.awb_21_i = purchase_untax_amt_svcph
            main_obj.awb_21_j = purchase_tax_amt_svcph - main_obj.awb_21_i
            main_obj.awb_21_k = purchase_untax_amt_svcaph
            main_obj.awb_21_l = purchase_tax_amt_svcaph - main_obj.awb_21_k
            main_obj.awb_21_m = purchase_untax_amt_exph + purchase_untax_amt_zph
            main_obj.awb_20_f = main_obj.awb_20_a + main_obj.awb_20_b \
                + main_obj.awb_20_c + main_obj.awb_20_d + main_obj.awb_20_e
            # question about total of 21p:
            main_obj.awb_21_p = main_obj.awb_21_a + main_obj.awb_21_b + main_obj.awb_21_c + main_obj.awb_21_d + main_obj.awb_21_e \
                + main_obj.awb_21_f + main_obj.awb_21_g + main_obj.awb_21_h + main_obj.awb_21_i \
                + main_obj.awb_21_j + main_obj.awb_21_k + main_obj.awb_21_l \
                + main_obj.awb_21_m + main_obj.awb_21_n + main_obj.awb_21_0
            main_obj.awb_22 = main_obj.awb_20_f + main_obj.awb_21_b + main_obj.awb_21_d + main_obj.awb_21_f \
                + main_obj.awb_21_h + main_obj.awb_21_j + main_obj.awb_21_l + main_obj.awb_21_0

    def _calculation_wizard_field(self):
        main_obj = self
        main_obj.awb_23_f = main_obj.awb_23_a + main_obj.awb_23_b + main_obj.awb_23_c \
            + main_obj.awb_23_d + main_obj.awb_23_e
        main_obj.awb_24 = main_obj.awb_22 - main_obj.awb_23_f
        main_obj.awb_25 = main_obj.awb_19_b - main_obj.awb_24
        main_obj.awb_26_h = main_obj.awb_26_a + main_obj.awb_26_b + main_obj.awb_26_c \
            + main_obj.awb_26_d + main_obj.awb_26_e + main_obj.awb_26_f + main_obj.awb_26_g
        main_obj.awb_27 = main_obj.awb_25 - main_obj.awb_26_h
        main_obj.awb_28_d = main_obj.awb_28_a + main_obj.awb_28_b + main_obj.awb_28_c
        main_obj.awb_29 = main_obj.awb_27 + main_obj.awb_28_d

    def unlink(self):
        for res in self:
            if res.awb_state != 'draft':
                raise UserError('You are allowed to delete only in Draft!')
        return super(Q2550, self).unlink()
        
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
