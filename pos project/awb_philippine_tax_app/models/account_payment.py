# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class tds_accounts(models.Model):
    _name = 'tds.accounts'
    _description = 'EWT ACCOUNTS'

    awb_tds_account_id = fields.Many2one('account.account', string="Difference Account",
                                     domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    awb_amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    amount = fields.Monetary(string='Payment Amount', required=True, store=True)
    tax_id = fields.Many2one('account.tax', string='Tax', required=True, )
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    payment_id = fields.Many2one('account.payment', string='Payment Record')


class tds_accounts_wizard(models.TransientModel):
    _name = 'tds.accounts.wizard'
    _description = 'EWT ACCOUNTS'

    awb_tds_account_id = fields.Many2one('account.account', string="Difference Account",
                                     domain=[('deprecated', '=', False)], copy=False, required="1")
    name = fields.Char('Description')
    awb_amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    amount = fields.Monetary(string='Payment Amount', required=True)
    tax_id = fields.Many2one('account.tax', string='Tax', required=True, )
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    awb_reg_id = fields.Many2one('account.payment.register', string='Payment Record')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    awb_tds = fields.Boolean(string='Apply EWT', default=False)
    awb_tds_tax_ids = fields.Many2many('account.tax', string='EWT')
    awb_tds_amt = fields.Float(string='EWT Amount', compute='compute_tds_amnt', store=True)
    awb_tax_amount = fields.Float(string='TAX Amount')
    # vendor_type = fields.Selection(related='partner_id.company_type', string='Partner Type')
    awb_vendor_type = fields.Char()
    awb_tds_multi_acc_ids = fields.One2many('tds.accounts', 'payment_id', string='Write Off Accounts')
    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
    )

    @api.onchange('awb_tds', 'payment_type')
    def _onchange_tds(self):
        print(self)
        if self.awb_tds:
            for rec in self:
                if rec.payment_type == 'outbound':
                    return {'domain': {
                        'awb_tds_tax_ids': [('type_tax_use', '=', 'sale'), ('awb_type', '=', 'ewt')]}}
                else:
                    return {'domain': {
                        'awb_tds_tax_ids': [('type_tax_use', '=', 'purchase'), ('awb_type', '=', 'ewt')]}}

    @api.onchange('awb_tds_tax_ids')
    def onchange_tds_tax_ids(self):
        self.write({'awb_tds_multi_acc_ids': [(5, 0, 0)]})
        # if not self._context.get('active_model'):
        #     return False
        amount_res = 0
        diff_amount = 0.0
        active_id = self._context.get('active_id')
        move = self.env['account.move'].browse(active_id)
        amount_res = move.amount_residual
        applicable = False
        for tds_tax in self.awb_tds_tax_ids:
            if move.partner_id and move.partner_id.tds_threshold_check:
                applicable = self.check_turnover(move.partner_id.id, tds_tax.payment_excess, amount_res)
            tax_repartition_lines = tds_tax.invoice_repartition_line_ids.filtered(
                lambda x: x.repartition_type == 'tax')
            taxes = tds_tax._origin.compute_all(
                amount_res)
            tds_tax_amount = taxes['total_included'] - taxes[
                'total_excluded'] if taxes else 0.0
            if applicable:
                if tds_tax.amount_type == 'group':
                    for child in tds_tax.children_tax_ids:
                        tax_repartition_lines = child.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        taxes = child._origin.compute_all(
                            self.amount)
                        tds_tax_amount = taxes['total_included'] - taxes[
                            'total_excluded'] if taxes else 0.0
                        self.awb_tds_multi_acc_ids.create({
                            'awb_tds_account_id': tax_repartition_lines._origin.id and tax_repartition_lines._origin.account_id.id,
                            'name': child.name,
                            'tax_id': child.id,
                            'amount': tds_tax_amount,
                            'payment_id': self.id
                        })
                else:
                    self.awb_tds_multi_acc_ids.create({
                        'awb_tds_account_id': tax_repartition_lines._origin.id and tax_repartition_lines._origin.account_id.id,
                        'name': tds_tax.name,
                        'tax_id': tds_tax._origin.id,
                        'amount': tds_tax_amount,
                        'payment_id': self.id
                    })
        diff_amount = sum([line.amount for line in self.awb_tds_multi_acc_ids])
        self.write({
            'amount': amount_res - diff_amount,
            'awb_tds_amt': diff_amount,
            # 'payment_difference_handling': 'reconcile',
        })

    @api.depends('awb_tds', 'awb_tds_tax_ids', 'amount')
    def compute_tds_amnt(self):
        for payment in self:
            payment.awb_tds_amt = 0.0
            if payment.awb_tds and payment.awb_tds_tax_ids and payment.amount:
                applicable = True
                total_tds_tax_amount = 0.0
                for tax in payment.awb_tds_tax_ids:
                    if payment.partner_id and payment.partner_id.tds_threshold_check:
                        for lines in self:
                            applicable = lines.check_turnover(lines.partner_id.id, tax.awb_payment_excess, lines.amount)
                    if applicable:
                        taxes = tax._origin.compute_all(
                            payment.amount)
                        total_tds_tax_amount += taxes['total_included'] - taxes[
                            'total_excluded'] if taxes else 0.0
                        payment.awb_tds_amt = total_tds_tax_amount
                    else:
                        payment.awb_tds_amt = 0.0
            else:
                payment.awb_tds_amt = 0.0

    def action_draft(self):
        super(AccountPayment, self).action_draft()
        self.write({'awb_tds': False})

    def check_turnover(self, partner_id, threshold, amount):
        if self.payment_type == 'outbound':
            domain = [('account_id.internal_type', '=', 'payable'),
                      ('move_id.state', '=', 'posted'), ('account_id.reconcile', '=', True)]
            journal_items = self.env['account.move.line'].search(domain)
            credits = sum([item.credit for item in journal_items])
            credits += amount
            if credits >= threshold:
                return True
            else:
                return False
        elif self.payment_type == 'inbound':
            domain = [('partner_id', '=', partner_id), ('account_id.internal_type', '=', 'receivable'),
                      ('move_id.state', '=', 'posted'), ('account_id.reconcile', '=', True)]
            journal_items = self.env['account.move.line'].search(domain)
            debits = sum([item.debit for item in journal_items])
            debits += amount
            if debits >= threshold:
                return True
            else:
                return False

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        if self.env.context.get('TDS'):
            self.awb_tds = True
        if self.awb_tds:
            if self.currency_id != self.company_id.currency_id:
                if self.payment_type == 'inbound' and self.partner_type == 'customer':
                    res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals=None)
                    converted_amt = self.currency_id._convert(self.amount,
                                                              self.company_id.currency_id,
                                                              self.company_id, self.date)

                    if self.env.context.get('tds_amount'):
                        tds_amount = self.company_id.currency_id._convert(self.env.context.get('tds_amount'),
                                                                          self.currency_id, self.company_id,
                                                                          self.date)
                        converted_tds_amt = self.env.context.get('tds_amount')
                    else:
                        converted_tds_amt = self.currency_id._convert(self.awb_tds_amt,
                                                                      self.company_id.currency_id,
                                                                      self.company_id, self.date)
                        tds_amount = self.awb_tds_amt

                    print('converted_amt', converted_amt, converted_tds_amt, tds_amount)
                    res[1]['credit'] = converted_amt - converted_tds_amt
                    res[1]['amount_currency'] = self.awb_tds_amt - self.amount
                    credit = converted_tds_amt
                    if self.env.context.get('awb_tds_tax_ids'):
                        for lines in self.env.context.get('awb_tds_tax_ids'):
                            for line in lines.invoice_repartition_line_ids:
                                if line.account_id:
                                    tds_lines = {
                                        'name': 'EWT',
                                        'amount_currency': -tds_amount,
                                        'currency_id': self.currency_id.id,
                                        'debit': -credit > 0.0 and credit or 0.0,
                                        'credit': credit if -credit < 0 else 0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': line.account_id.id,
                                    }
                                    res.append(tds_lines)
                    else:
                        for lines in self.awb_tds_tax_ids:
                            for line in lines.invoice_repartition_line_ids:
                                if line.account_id:
                                    tds_lines = {
                                        'name': 'EWT',
                                        'amount_currency': -tds_amount,
                                        'currency_id': self.currency_id.id,
                                        'debit': -credit > 0.0 and credit or 0.0,
                                        'credit': credit if -credit < 0 else 0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': line.account_id.id,
                                    }
                                    res.append(tds_lines)
                    return res

                if self.payment_type == 'outbound' and self.partner_type == 'supplier':
                    print("outboundotbount")
                    res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals=None)
                    converted_amt = self.currency_id._convert(self.amount,
                                                              self.company_id.currency_id,
                                                              self.company_id, self.date)
                    if self.env.context.get('tds_amount'):
                        tds_amount = self.company_id.currency_id._convert(self.env.context.get('tds_amount'),
                                                                          self.currency_id, self.company_id,
                                                                          self.date)
                        converted_tds_amt = self.env.context.get('tds_amount')
                    else:
                        converted_tds_amt = self.currency_id._convert(self.awb_tds_amt,
                                                                      self.company_id.currency_id,
                                                                      self.company_id, self.date)
                        tds_amount = self.awb_tds_amt
                    res[1]['debit'] = converted_amt - converted_tds_amt
                    debit = converted_tds_amt
                    if self.env.context.get('awb_tds_tax_ids'):
                        for lines in self.env.context.get('awb_tds_tax_ids'):
                            for line in lines.invoice_repartition_line_ids:
                                if line.account_id:
                                    tds_lines = {
                                        'name': 'EWT',
                                        'amount_currency': tds_amount,
                                        'currency_id': self.currency_id.id,
                                        'debit': debit,
                                        'credit': 0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': line.account_id.id,
                                    }
                                    res.append(tds_lines)
                    else:
                        for lines in self.awb_tds_tax_ids:
                            for line in lines.invoice_repartition_line_ids:
                                if line.account_id:
                                    tds_lines = {
                                        'name': 'EWT',
                                        'amount_currency': tds_amount,
                                        'currency_id': self.currency_id.id,
                                        'debit': debit,
                                        'credit': 0,
                                        'partner_id': self.partner_id.id,
                                        'account_id': line.account_id.id,
                                    }
                                    res.append(tds_lines)

                    return res
            elif self.env.context.get('TDS'):
                return super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
            else:
                if self.payment_type == 'inbound' and self.partner_type == 'customer':
                    res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals=None)
                    for lines in self.awb_tds_tax_ids:
                        tax_am = (self.amount / 100) * lines.amount
                        res[1]['credit'] = res[1]['credit'] - tax_am
                        if lines.invoice_repartition_line_ids.account_id:
                            tds_lines = {
                                'name': 'EWT',
                                'amount_currency': -self.awb_tds_amt,
                                'currency_id': self.currency_id.id,
                                'debit': 0.0,
                                'credit': tax_am if -tax_am < 0 else 0,
                                'partner_id': self.partner_id.id,
                                'account_id': lines.invoice_repartition_line_ids.account_id.id,
                            }
                            res.append(tds_lines)
                    return res
                print(self.payment_type,'==========res',self.partner_type)
                if self.payment_type == 'outbound' and self.partner_type == 'supplier':
                    res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals=None)
                    for lines in self.awb_tds_tax_ids:
                        tax_am = (self.amount / 100) * lines.amount
                        res[1]['debit'] = res[1]['debit'] - tax_am
                        for line in lines.invoice_repartition_line_ids:
                            if line.account_id:
                                tds_lines = {
                                    'name': 'EWT',
                                    'amount_currency': self.awb_tds_amt,
                                    'currency_id': self.currency_id.id,
                                    'debit': tax_am if -tax_am < 0 else 0,
                                    'credit': 0,
                                    'partner_id': self.partner_id.id,
                                    'account_id': line.account_id.id,
                                }
                                res.append(tds_lines)
                    return res
        else:
            return super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)

    def _synchronize_from_moves(self, changed_fields):
        if self._context.get('skip_account_move_synchronization'):
            return
        for pay in self.with_context(skip_account_move_synchronization=True):
            if pay.move_id.statement_line_id:
                continue
            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}
            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))
            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    awb_tds = fields.Boolean(string='Apply EWT', default=False)
    awb_tds_tax_ids = fields.Many2many('account.tax', string='EWT')
    awb_tds_amt = fields.Float(string='EWT Amount')#, compute='compute_tds_amount')
    tax_amount = fields.Float(string='TAX Amount')
    # vendor_type = fields.Selection(related='partner_id.company_type', string='Partner Type')
    awb_vendor_type = fields.Char()
    awb_tds_multi_acc_ids = fields.One2many('tds.accounts.wizard', 'awb_reg_id', string='Write Off Accounts')
    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
    )

    def _create_payments(self):
        if self.awb_tds:
            context = self.env.context.copy()
            context.update({'TDS': True, 'tds_amount': sum(self.awb_tds_multi_acc_ids.mapped('amount')),
                            'awb_tds_tax_ids': self.awb_tds_tax_ids})
            self.env.context = context
            res = super(AccountPaymentRegister, self)._create_payments()
            for ids in self.awb_tds_tax_ids:
                res.awb_tds_tax_ids = ids
            res.tds = True
            res.awb_tds_amt = self.payment_difference
            if self.currency_id != self.company_id.currency_id:
                tds_amount = sum(self.awb_tds_multi_acc_ids.mapped('amount'))
                tds_amount = self.company_id.currency_id._convert(tds_amount, self.currency_id, self.company_id,
                                                                  self.payment_date)
                res.awb_tds_amt = tds_amount
            return res
        else:
            return super(AccountPaymentRegister, self)._create_payments()

    def _create_payment_vals_from_wizard(self):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        if not self.currency_id.is_zero(self.payment_difference) and self.awb_tds:
            write_off_vals = []
            for woff_payment in self.awb_tds_multi_acc_ids:
                write_off_vals.append({
                    'name': woff_payment.name,
                    'amount': woff_payment.amount or 0.0,
                    'account_id': woff_payment.awb_tds_account_id.id,
                    'is_multi_write_off': True
                })
                if not res['write_off_line_vals']['account_id']:
                    res['write_off_line_vals']['account_id'] = woff_payment.awb_tds_account_id.id
                    res['write_off_line_vals']['name'] = woff_payment.name
        return res

    @api.onchange('awb_tds_tax_ids')
    def onchange_tds_tax_ids(self):
        self.write({'awb_tds_multi_acc_ids': [(5, 0, 0)]})
        if not self._context.get('active_model'):
            return False
        amount_res = 0
        diff_amount = 0.0
        active_id = self._context.get('active_id')
        move = self.env['account.move'].browse(active_id)
        self.compute_tds_amount()
        amount_res = move.amount_residual
        applicable = False
        for tds_tax in self.awb_tds_tax_ids:
            if move.partner_id and move.partner_id.tds_threshold_check:
                applicable = self.check_turnover(move.partner_id.id, tds_tax.awb_payment_excess, amount_res)
            tax_repartition_lines = tds_tax.invoice_repartition_line_ids.filtered(
                lambda x: x.repartition_type == 'tax')
            taxes = tds_tax._origin.compute_all(
                amount_res)
            tds_tax_amount = taxes['total_included'] - taxes[
                'total_excluded'] if taxes else 0.0
            if applicable:
                if tds_tax.amount_type == 'group':
                    for child in tds_tax.children_tax_ids:
                        tax_repartition_lines = child.invoice_repartition_line_ids.filtered(
                            lambda x: x.repartition_type == 'tax')
                        taxes = child._origin.compute_all(
                            self.amount)
                        tds_tax_amount = taxes['total_included'] - taxes[
                            'total_excluded'] if taxes else 0.0
                        res = self._create_payments()
                        lines = res._prepare_move_line_default_vals()
                        self.awb_tds_multi_acc_ids.create({
                            'awb_tds_account_id': tax_repartition_lines._origin.id and tax_repartition_lines._origin.account_id.id,
                            'name': child.name,
                            'tax_id': child.id,
                            'amount': tds_tax_amount,
                            'currency_id': self.currency_id.id,
                            'reg': self.id
                        })
                        print(self.awb_tds_multi_acc_ids,"================1111",tds_tax_amount)
                else:
                    vals = {
                        'awb_tds_account_id': tax_repartition_lines._origin.id and tax_repartition_lines._origin.account_id.id,
                        'name': tds_tax.name,
                        'tax_id': tds_tax._origin.id,
                        'amount': tds_tax_amount,
                        'currency_id': self.currency_id.id,
                        'awb_reg_id': self.id,
                    }
                    result = self.env['tds.accounts.wizard'].create(vals)
        for line in self.awb_tds_multi_acc_ids:
            diff_amount = sum([line.amount for line in self.awb_tds_multi_acc_ids])
        self.write({
            'amount': amount_res - diff_amount,
            'awb_tds_amt': diff_amount,
            'payment_difference_handling': 'reconcile',
        })

    @api.depends('awb_tds', 'awb_tds_tax_ids', 'amount')
    def compute_tds_amount(self):
        for payment in self:
            payment.awb_tds_amt = 0.0
            if payment.awb_tds and payment.awb_tds_tax_ids and payment.amount:
                applicable = True
                total_tds_tax_amount = 0.0
                for tax in payment.awb_tds_tax_ids:
                    if payment.partner_id and payment.partner_id.tds_threshold_check:
                        applicable = self.check_turnover(self.partner_id.id, tax.awb_payment_excess, self.amount)
                    if applicable:
                        taxes = tax._origin.compute_all(
                            payment.amount)
                        total_tds_tax_amount += taxes['total_included'] - taxes[
                            'total_excluded'] if taxes else 0.0
                        payment.awb_tds_amt = total_tds_tax_amount
                    else:
                        payment.awb_tds_amt = 0.0
            else:
                payment.awb_tds_amt = 0.0

    def action_draft(self):
        super(AccountPayment, self).action_draft()
        self.write({'tds': False})

    def check_turnover(self, partner_id, threshold, amount):
        active_id = self._context.get('active_id')
        move = self.env['account.move'].browse(active_id)
        amount_res = move.amount_residual
        if self.payment_type == 'outbound':
            domain = [('partner_id', '=', partner_id), ('account_id.internal_type', '=', 'payable'),
                      ('move_id.state', '=', 'posted'), ('account_id.reconcile', '=', True)]
            journal_items = self.env['account.move.line'].search(domain)
            credits = sum([item.credit for item in journal_items])
            credits += amount
            if credits >= threshold:
                return True
            else:
                return False
        elif self.payment_type == 'inbound':
            domain = [('partner_id', '=', partner_id), ('account_id.internal_type', '=', 'receivable'),
                      ('move_id.state', '=', 'posted'), ('account_id.reconcile', '=', True)]
            journal_items = self.env['account.move.line'].search(domain)
            debits = sum([item.debit for item in journal_items])
            debits += amount
            if debits >= threshold:
                return True
            else:
                return False
