# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    awb_vat_registration_status = fields.Selection([
        ('unregistered', 'Unregistered'),
        ('registered', 'Registered'),
        ('vat_Exempt', 'VATExempt'),
    ], string="VAT Registration Status", default='unregistered')
    awb_tax_based_on = fields.Selection([('untaxed', 'Untaxed')], string='Tax Based On',
                                    default='untaxed')

    tds = fields.Boolean('Apply EWT', default=False,
                         states={'draft': [('readonly', False)]})
    awb_tds_tax_ids = fields.Many2many('account.tax', string='EWT',
                                   states={'draft': [('readonly', False)]})
    awb_tds_amt = fields.Monetary(string='EWT Amount',
                              readonly=True, compute='_compute_ewt_amount')
    awb_total_gross = fields.Monetary(string='Total',
                                  store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string='VAT',
                                  store=True, readonly=True, compute='_compute_ewt_amount')
    amount_total = fields.Monetary(string='Total',
                                  store=True, readonly=True, compute='_compute_ewt_amount')
    awb_amount_total = fields.Monetary(string='Net Total',
                                   store=True, readonly=True, compute='_compute_ewt_amount')
    # awb_vendor_type = fields.Selection(related='partner_id.company_type', string='Partner Type')
    awb_vendor_type = fields.Char()
    awb_display_in_report = fields.Boolean('Display EWT in Report', default=False)

    @api.depends('line_ids.awb_tds_tax_ids','amount_total','amount_tax')
    def _compute_ewt_amount(self):
        total_ewt = 0
        total_tax = 0
        for line in self:
            if line.invoice_line_ids:
                for rec in line.invoice_line_ids:
                    total_ewt += rec.quantity * rec.price_unit * rec.awb_tds_tax_ids.amount / 100
                    total_tax += rec.quantity * rec.price_subtotal * rec.tax_ids.amount / 100
                    line.awb_tds_amt = total_ewt
                    line.amount_tax = total_tax
                    line.amount_total = line.amount_untaxed + line.amount_tax
                    line.awb_amount_total = line.amount_total - line.awb_tds_amt
                    line.awb_total_gross = line.amount_untaxed + line.amount_tax
            else:
                line.awb_tds_amt = 0


    def check_turnover(self, partner_id, threshold, awb_total_gross):
        domain = [('partner_id', '=', partner_id), ('account_id.internal_type', '=', 'payable'),
                  ('move_id.state', '=', 'posted'), ('account_id.reconcile', '=', True)]
        journal_items = self.env['account.move.line'].search(domain)
        credits = sum([item.credit for item in journal_items])
        credits += awb_total_gross
        if credits >= threshold:
            return True
        else:
            return False

    @api.onchange(
        'invoice_line_ids.awb_tds_tax_ids', 
        'line_ids.debit',
        'invoice_line_ids.price_unit',
        'line_ids.credit',
        'invoice_line_ids.tax_ids')
    def _onchange_tds_tax_id(self):
        self._recompute_tax_lines()
        for invoice in self:
            for rec in invoice.invoice_line_ids:
                if not rec.awb_tds_tax_ids:
                    existing_lines = invoice.line_ids.filtered(lambda x: x.awb_tds_tag)
                    existing_lines.credit = 0
                    existing_lines.debit = 0
                    invoice.line_ids -= existing_lines
                    invoice._onchange_recompute_dynamic_lines()
            tax_ids = []
            tds_list = []
            for line in self.invoice_line_ids:
                for tax in line.awb_tds_tax_ids:
                    applicable = True
                    # if invoice.partner_id and invoice.partner_id.tds_threshold_check:
                    #     applicable = invoice.check_turnover(invoice.partner_id.id, tax.awb_payment_excess,
                    #                                         invoice.awb_total_gross)
                    tax_repartition_lines = tax.invoice_repartition_line_ids.filtered(
                        lambda x: x.repartition_type == 'tax') if tax else None
                    tds_amount = abs(invoice.awb_tds_amt) if tax and applicable else 0
                    tds_tax = tax if tax else None
                    taxes = tax._origin.compute_all(
                        invoice.amount_untaxed)
                    tds_tax_amount = line.quantity * line.price_unit * line.awb_tds_tax_ids.amount / 100
                    converted_tds_tax_amount = self.currency_id._convert(tds_tax_amount,
                                                                         self.company_id.currency_id,
                                                                         self.company_id, self.date)
                    tag_ids = []
                    for tax_rec in taxes.get('taxes'):
                        if tax._origin.id == tax_rec.get('id'):
                            tag_ids = (tax_rec.get('tax_tag_ids'))
                    credit = 0
                    debit = 0
                    if invoice.move_type in ['in_invoice', 'out_refund', 'in_receipt']:
                        credit = converted_tds_tax_amount
                    elif invoice.move_type in ['out_invoice', 'in_refund', 'out_receipt']:
                        debit = converted_tds_tax_amount
                    print(taxes,'==============taxes',converted_tds_tax_amount)
                    existing_lines = self.env['account.move.line']
                    if tax.amount_type == 'group':
                        for child in tax.children_tax_ids:
                            tax_ids.append(child.name)
                            existing_lines = invoice.line_ids.filtered(lambda x: x.awb_tds_tag and x.name == child.name)
                    else:
                        tax_ids.append(tax.name)
                        existing_lines = invoice.line_ids.filtered(lambda x: x.awb_tds_tag and x.name == tax.name)
                    for ex_line in invoice.line_ids.filtered(lambda x: x.awb_tds_tag):
                        if ex_line.name not in tds_list:
                            invoice.line_ids -= ex_line
                    if applicable and tds_tax_amount and tds_tax and tax_repartition_lines and not existing_lines:
                        create_method = invoice.env['account.move.line'].new
                        for rec in self.invoice_line_ids:
                            tds_tax_amount = rec.quantity * rec.price_unit * rec.awb_tds_tax_ids.amount / 100
                            if tds_tax.amount_type == 'group':
                                for child in tds_tax.children_tax_ids:
                                    tax_repartition_lines = child.invoice_repartition_line_ids.filtered(
                                        lambda x: x.repartition_type == 'tax') if child else None
                                    tds_amount = child.amount * (invoice.awb_total_gross / 100)
                                    taxes = child._origin.compute_all(
                                        invoice.awb_total_gross)
                                    for tax_rec in taxes.get('taxes'):
                                        if child._origin.id == tax_rec.get('id'):
                                            tag_ids = tax_rec.get('tax_tag_ids')
                                    tds_tax_amount = taxes['total_included'] - taxes[
                                        'total_excluded'] if taxes else 0
                                    converted_tds_tax_amount = invoice.currency_id._convert(tds_tax_amount,
                                                                                         self.company_id.currency_id,
                                                                                         self.company_id, self.date)
                                    if invoice.type in ['in_invoice', 'out_refund', 'in_receipt']:
                                        credit = converted_tds_tax_amount
                                    elif invoice.type in ['out_invoice', 'in_refund', 'out_receipt']:
                                        debit = converted_tds_tax_amount
                                    if invoice.move_type in ['in_invoice', 'out_refund', 'in_receipt']:
                                        print(debit,credit,"1==================tax",tax.name)
                                        create_method({
                                            'name': rec.awb_tds_tax_ids.name,
                                            'debit': debit,
                                            'credit': tds_tax_amount,
                                            'quantity': rec.quantity,
                                            'amount_currency': -tds_tax_amount,
                                            'date_maturity': invoice.invoice_date,
                                            'move_id': invoice.id,
                                            # 'currency_id': invoice.currency_id.id if invoice.currency_id != invoice.company_id.currency_id else False,
                                            'account_id': tax_repartition_lines.account_id.id if tax_repartition_lines else None,
                                            'partner_id': invoice.commercial_partner_id.id,
                                            'awb_tds_tag': True,
                                            'tax_id': tax.id,
                                            'tax_ids': [(6, 0, tax.ids)],
                                            'tax_tag_ids': [(6, 0, tag_ids)],
                                            'exclude_from_invoice_tab': True,
                                        })
                                    elif invoice.move_type in ['out_invoice', 'in_refund', 'out_receipt']:
                                        print(debit,credit,"2==================tax",tax.name)
                                        create_method({
                                            'name': rec.awb_tds_tax_ids.name,
                                            'debit': tds_tax_amount,
                                            'credit': credit,
                                            'quantity': rec.quantity,
                                            'amount_currency': tds_tax_amount,
                                            'date_maturity': invoice.invoice_date,
                                            'move_id': invoice.id,
                                            # 'currency_id': invoice.currency_id.id if invoice.currency_id != invoice.company_id.currency_id else False,
                                            'account_id': tax_repartition_lines.account_id.id if tax_repartition_lines else None,
                                            'partner_id': invoice.commercial_partner_id.id,
                                            'awb_tds_tag': True,
                                            'tax_id': tax.id,
                                            'tax_ids': [(6, 0, tax.ids)],
                                            'tax_tag_ids': [(6, 0, tag_ids)],
                                            'exclude_from_invoice_tab': True,
                                        })
                            else:
                                if invoice.move_type in ['in_invoice', 'out_refund', 'in_receipt'] and rec.awb_tds_tax_ids.name != False:
                                    print(debit,credit,"3==================tax",tax.name)
                                    create_method({
                                        'name': rec.awb_tds_tax_ids.name,
                                        'debit': debit,
                                        'credit': tds_tax_amount,
                                        'quantity': rec.quantity,
                                        'amount_currency': -tds_tax_amount,
                                        'date_maturity': invoice.invoice_date,
                                        'move_id': invoice.id,
                                        # 'currency_id': invoice.currency_id.id if invoice.currency_id != invoice.company_id.currency_id else False,
                                        'account_id': rec.awb_tds_tax_ids.invoice_repartition_line_ids.account_id if tax_repartition_lines else None,
                                        'partner_id': invoice.commercial_partner_id.id,
                                        'tax_ids': [(6, 0, tax.ids)],
                                        'awb_tds_tag': True,
                                        'awb_tax_id': tax.id,
                                        'exclude_from_invoice_tab': True,
                                    })
                                elif invoice.move_type in ['out_invoice', 'in_refund', 'out_receipt'] and rec.awb_tds_tax_ids.name != False:
                                    print(debit,credit,"4==================tax",tax.name)
                                    create_method({
                                        'name': rec.awb_tds_tax_ids.name,
                                        'debit': tds_tax_amount,
                                        'credit': credit,
                                        'quantity': rec.quantity,
                                        'amount_currency': tds_tax_amount,
                                        'date_maturity': invoice.invoice_date,
                                        'move_id': line.move_id.id,
                                        # 'currency_id': invoice.currency_id.id if invoice.currency_id != invoice.company_id.currency_id else False,
                                        'account_id': rec.awb_tds_tax_ids.invoice_repartition_line_ids.account_id if tax_repartition_lines else None,
                                        'partner_id': invoice.commercial_partner_id.id,
                                        'tax_ids': [(6, 0, tax.ids)],
                                        'awb_tds_tag': True,
                                        'awb_tax_id': tax.id,
                                        'exclude_from_invoice_tab': True,
                                    })
                    invoice._onchange_recompute_dynamic_lines()

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        for rec in self:
            rec.ensure_one()
            in_draft_mode = rec != rec._origin

        def _serialize_tax_grouping_key(grouping_dict):
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            move = base_line.move_id
            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                is_refund = move.move_type in ('out_refund', 'in_refund')
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
                price_unit_wo_discount = base_line.amount_currency
            return base_line.tax_ids._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=move.always_tax_exigible,
            )
            
        taxes_map = {}

        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(
                    tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'],
                                                                                       tax_repartition_line,
                                                                                       tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict

        taxes_map = self._preprocess_taxes_map(taxes_map)

        for taxes_map_entry in taxes_map.values():
            if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

            if currency.is_zero(taxes_map_entry['amount']):
                if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id,
                                                self.company_id, self.date or fields.Date.context_today(self))

            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
                continue
            tax = 0
            balance = currency._convert(
                taxes_map_entry['amount'],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )
            to_write_on_line = {
                'amount_currency': taxes_map_entry['amount'],
                'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }            
            if taxes_map_entry['tax_line']:
                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env[
                    'account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                taxes_map_entry['tax_line'].update(
                    taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        res = super(AccountMove, self)._onchange_invoice_line_ids()
        self._onchange_tds_tax_id()
        return res


class AccountInvoiceTax(models.Model):
    _inherit = "account.tax"

    awb_tds = fields.Boolean('EWT', default=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.awb_vat_registration_status = self.partner_id.awb_vat_registration_status
        else:
            self.awb_vat_registration_status = 'unregistered'
        return super(AccountMove, self)._onchange_partner_id()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    awb_tds_tag = fields.Boolean("EWT Tag", default=False)
    awb_tax_id = fields.Many2one('account.tax', string='Tax')
    awb_tds_tax_ids = fields.Many2many('account.tax','rel_awb_wet','awb_id', 'wet_id', string='EWT')
    awb_ewt_total = fields.Float("Total(With EWT)", compute='_compute_wet')

    @api.depends('awb_tds_tax_ids')
    def _compute_wet(self):
        for rec in self:
            if rec.awb_tds_tax_ids:
                total_ewt = rec.quantity * rec.price_unit * rec.awb_tds_tax_ids.amount / 100
                rec.awb_ewt_total = rec.price_total - total_ewt
            else:
                rec.awb_ewt_total = 0


    @api.onchange('tax_ids', 'awb_tds_tax_ids')
    def _onchange_mark_recompute_taxes(self):
        super(AccountMoveLine, self)._onchange_mark_recompute_taxes()
        if len(self.tax_ids) > 1:
            raise UserError(
                ("You cannot enter more than one tax"))
        if len(self.awb_tds_tax_ids) > 1:
            raise UserError(
                ("You cannot enter more than one EWT"))
