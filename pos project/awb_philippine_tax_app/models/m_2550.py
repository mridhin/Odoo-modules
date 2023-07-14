# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import calendar
from odoo.exceptions import ValidationError, UserError


class M2550(models.Model):
    _name = "m.2550"
    _description = "2550M"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    awb_company_id = fields.Many2one('res.company', string='Company')
    awb_partner_id = fields.Many2one('res.partner', string='Partner')
    awb_journal_id = fields.Many2one('account.journal', string='Journal')
    awb_fiscal_year = fields.Many2one(
        'account.fiscal.year', string='Fiscal Year')
    awb_fiscal_month = fields.Many2one(
        'account.month.period', string='Fiscal Month')
    awb_month = fields.Char('Month')
    awb_year = fields.Char('Year')
    awb_entry_count = fields.Boolean(
        'Entry Count', default=False, compute='_check_journal_entry')
    awb_move_id = fields.Many2one('account.move',
                                  string='Journal Entry',
                                  )
    # Visible
    awb_amended_return = fields.Selection(
        [('t', 'Yes'), ('f', 'No')], 'Amended Return', default='f')
    awb_no_of_Sheets = fields.Integer('Sheets Attached')
    awb_special_tax_or_inter_tax_treaty = fields.Selection(
        [('y', 'Yes'), ('n', 'No')],
        string='tax relief under Special Law or International Tax Treaty', default='n')
    awb_specify = fields.Char('If Yes, please specify')
    awb_12_a = fields.Float('12A')
    awb_12_b = fields.Float('12B')
    awb_13_a = fields.Float('13A')
    awb_13_b = fields.Float('13B')
    awb_14 = fields.Float('14 Zero Rated Sales/Receipts')
    awb_15 = fields.Float('15 Exempt Sales/Receipts')
    awb_16_a = fields.Float('16A')
    awb_16_b = fields.Float('16B')
    awb_17_a = fields.Float(
        '17A Input Tax Carried Over from Previous Period')
    awb_17_b = fields.Float(
        '17B Input Tax Deferred on Capital '
        'Goods Exceeding P1Million from Previous Period')
    awb_17_c = fields.Float('17C Transitional Input Tax')
    awb_17_d = fields.Float('17D Presumptive Input Tax')
    awb_17_e = fields.Float('17E Others')
    awb_17_f = fields.Float('17F Total')
    awb_18_a = fields.Float('18A')
    awb_18_b = fields.Float('18B')
    awb_18_c = fields.Float('18C')
    awb_18_d = fields.Float('18D')
    awb_18_e = fields.Float('18E')
    awb_18_f = fields.Float('18F')
    awb_18_g = fields.Float('18G')
    awb_18_h = fields.Float('18H')
    awb_18_i = fields.Float('18I')
    awb_18_j = fields.Float('18J')
    awb_18_k = fields.Float('18K')
    awb_18_l = fields.Float('18L')
    awb_18_m = fields.Float('18M')
    awb_18_n = fields.Float('18N')
    awb_18_O = fields.Float('18O')
    awb_18_p = fields.Float('18P')
    awb_19 = fields.Float('19 Total Available Input Tax')
    awb_20_a = fields.Float('20A')
    awb_20_b = fields.Float('20B')
    awb_20_c = fields.Float('20C')
    awb_20_d = fields.Float('20D')
    awb_20_e = fields.Float('20E')
    awb_20_f = fields.Float('20F')
    awb_21 = fields.Float('21 Total Allowable Input Tax')
    awb_22 = fields.Float('22 Net VAT Payable')
    awb_23_a = fields.Float('23A')
    awb_23_b = fields.Float('23B')
    awb_23_c = fields.Float('23C')
    awb_23_d = fields.Float('23D')
    awb_23_e = fields.Float('23E')
    awb_23_f = fields.Float('23F')
    awb_23_g = fields.Float('23G')
    awb_24 = fields.Float('24 Tax Still Payable/(Overpayment)')
    awb_25_a = fields.Float('25A')
    awb_25_b = fields.Float('25B')
    awb_25_c = fields.Float('25C')
    awb_25_d = fields.Float('25D')
    awb_26 = fields.Float('26 Total Amount Payable/(Overpayment)')
    awb_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('amendment', 'Amendment')], tracking=True,
        required=True, readonly=True, default='draft', copy=False)

    # method is use to validate a state
    def action_validate(self):
        self.write({'awb_state': 'validated'})

    # method is use for set a state in Draft state
    def action_resetdraft(self):
        self.write({'awb_state': 'draft'})

    @api.onchange('awb_fiscal_month')
    def get_month_year(self):
        seq = self.awb_fiscal_month.sequence
        code = str(self.awb_fiscal_month.code)
        year = code[3:]
        self.awb_month = code[0:2]
        self.awb_year = year

    @api.depends('awb_entry_count')
    def _check_journal_entry(self):
        if self.awb_move_id:
            self.awb_entry_count = True
        else:
            self.awb_entry_count = False

    def action_report(self):
        # Method to M2550 report
        # if not data_list:
        # raise UserError(_('No records found'))
        # else:
        return self.env.ref(
            'awb_philippine_tax_app.action_report_m_2550_report'
        ).report_action([])

    # method is use for data calculation
    def sale_ammount_tax_count(self):
        main_obj = self
        start_date = main_obj.awb_fiscal_month.date_start
        end_date = main_obj.awb_fiscal_month.date_stop
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
        main_obj.awb_12_a = sale_untax_amt_sph
        main_obj.awb_12_b = sale_tax_amt_sph - sale_untax_amt_sph
        main_obj.awb_13_a = sale_untax_amt_gph
        main_obj.awb_13_b = sale_tax_amt_gph - sale_untax_amt_gph
        main_obj.awb_14 = sale_untax_amt_zph
        main_obj.awb_15 = sale_untax_amt_exph
        main_obj.awb_16_a = main_obj.awb_12_a + main_obj.awb_13_a + main_obj.awb_14 + main_obj.awb_15
        main_obj.awb_16_b = main_obj.awb_12_b + main_obj.awb_13_b

    def purchase_ammount_tax_count(self):
        main_obj = self
        start_date = main_obj.awb_fiscal_month.date_start
        end_date = main_obj.awb_fiscal_month.date_stop
        company = main_obj.awb_company_id
        domain = [
            ('move_id.invoice_date', '>=', start_date),
            ('move_id.invoice_date', '<=', end_date),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', company.id)
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
            main_obj.awb_18_a = purchase_untax_amt_capph_moreless1m
        if purchase_untax_amt_capph_moreless1m >= 1000000:
            main_obj.awb_18_c = purchase_untax_amt_capph_moreless1m
        if purchase_tax_amt_capph_moreless1m < 1000000:
            main_obj.awb_18_b = purchase_tax_amt_capph_moreless1m - main_obj.awb_18_a
        if purchase_tax_amt_capph_moreless1m >= 1000000:
            main_obj.awb_18_d = purchase_tax_amt_capph_moreless1m - main_obj.awb_18_c
        main_obj.awb_18_e = purchase_untax_amt_sph
        main_obj.awb_18_f = purchase_tax_amt_sph - main_obj.awb_18_e
        main_obj.awb_18_g = purchase_untax_amt_imptph
        main_obj.awb_18_h = purchase_tax_amt_imptph - main_obj.awb_18_g
        main_obj.awb_18_i = purchase_untax_amt_svcph
        main_obj.awb_18_j = purchase_tax_amt_svcph - main_obj.awb_18_i
        main_obj.awb_18_k = purchase_untax_amt_svcaph
        main_obj.awb_18_l = purchase_tax_amt_svcaph - main_obj.awb_18_k
        main_obj.awb_18_m = purchase_untax_amt_exph + purchase_untax_amt_zph
        main_obj.awb_17_f = main_obj.awb_17_a + main_obj.awb_17_b \
            + main_obj.awb_17_c + main_obj.awb_17_d + main_obj.awb_17_e
        # Question about 18p total:
        main_obj.awb_18_p = main_obj.awb_18_a + main_obj.awb_18_b + main_obj.awb_18_c + main_obj.awb_18_d + main_obj.awb_18_e \
            + main_obj.awb_18_f + main_obj.awb_18_g + main_obj.awb_18_h + main_obj.awb_18_i \
            + main_obj.awb_18_j + main_obj.awb_18_k + main_obj.awb_18_l \
            + main_obj.awb_18_m + main_obj.awb_18_n + main_obj.awb_18_O
        main_obj.awb_19 = main_obj.awb_17_f + main_obj.awb_18_b + main_obj.awb_18_d + main_obj.awb_18_f \
            + main_obj.awb_18_h + main_obj.awb_18_j + main_obj.awb_18_l + main_obj.awb_18_O

    def calculation_wizard_field(self):
        main_obj = self
        main_obj.awb_20_f = main_obj.awb_20_a + main_obj.awb_20_b + main_obj.awb_20_c \
            + main_obj.awb_20_d + main_obj.awb_20_e
        main_obj.awb_21 = main_obj.awb_19 - main_obj.awb_20_f
        main_obj.awb_22 = main_obj.awb_16_b - main_obj.awb_21
        main_obj.awb_23_g = main_obj.awb_23_a + main_obj.awb_23_b + main_obj.awb_23_c \
            + main_obj.awb_23_d + main_obj.awb_23_e + main_obj.awb_23_f
        main_obj.awb_24 = main_obj.awb_22 - main_obj.awb_23_g
        main_obj.awb_25_d = main_obj.awb_25_a + main_obj.awb_25_b + main_obj.awb_25_c
        main_obj.awb_26 = main_obj.awb_24 + main_obj.awb_25_d

    def action_generate_report(self):
        self.sale_ammount_tax_count()
        self.purchase_ammount_tax_count()
        self.calculation_wizard_field()

    def unlink(self):
        for res in self:
            if res.awb_state != 'draft':
                raise UserError('You are allowed to delete only in Draft!')
        return super(M2550, self).unlink()

    def generate_journal_Entry(self):
        partner = self.awb_partner_id
        journal = self.awb_journal_id
        output_16b = self.awb_16_b
        input_21 = self.awb_21
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
            if output_16b < input_21:
                line_values_debit.update({'debit': output_16b})
                line_values_credit.update({'credit': input_21})
                line_values_payble.update({'debit': input_21 - output_16b})
            elif output_16b > input_21:
                line_values_debit.update({'debit': output_16b})
                line_values_credit.update({'credit': input_21})
                line_values_payble.update({'credit': output_16b - input_21})
            else:
                pass
            line = {
                'move_type': 'entry',
                'company_id': self.awb_company_id.id,
                'awb_vat_registration_status':
                partner.awb_vat_registration_status or 'unregistered',
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

    # Method Redirect to jouranl page which is created by user
    def action_view_journal_entry(self):
        context = dict(self._context or {})
        wiz_form_id = self.env['ir.model.data'].get_object_reference(
            'account', 'view_move_form')[1]
        if self.awb_move_id:
            return {
                'view_type': 'form',
                'view_id': wiz_form_id,
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.awb_move_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': context,
            }
