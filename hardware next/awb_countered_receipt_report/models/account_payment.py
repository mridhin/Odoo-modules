# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#  import from odoo lib
from odoo import models, api 
from odoo.exceptions import UserError
from odoo.osv import expression

#Reconcile button action for payment table
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def reconcile(self):
        ''' Reconcile the current move lines all together.
        :return: A dictionary representing a summary of what has been done during the reconciliation:
                * partials:             A recorset of all account.partial.reconcile created during the reconciliation.
                * full_reconcile:       An account.full.reconcile record created when there is nothing left to reconcile
                                        in the involved lines.
                * tax_cash_basis_moves: An account.move recordset representing the tax cash basis journal entries.
        '''
        results = {}
        if not self:
            return results

        # List unpaid invoices
        not_paid_invoices = self.move_id.filtered(
            lambda move: move.is_invoice(include_receipts=True) and move.payment_state not in ('paid', 'in_payment')
        )

        # ==== Check the lines can be reconciled together ====
        company = None
        account = None
        for line in self:
            if line.reconciled:
                raise UserError(_("You are trying to reconcile some entries that are already reconciled."))
            if not line.account_id.reconcile and line.account_id.internal_type != 'liquidity':
                raise UserError(_("Account %s does not allow reconciliation. First change the configuration of this account to allow it.")
                                % line.account_id.display_name)
            if line.move_id.state not in ['ctr_receipt','posted']:
                raise UserError(_('You can only reconcile posted entries.'))
            if company is None:
                company = line.company_id
            elif line.company_id != company:
                raise UserError(_("Entries doesn't belong to the same company: %s != %s")
                                % (company.display_name, line.company_id.display_name))
            if account is None:
                account = line.account_id
            elif line.account_id != account:
                raise UserError(_("Entries are not from the same account: %s != %s")
                                % (account.display_name, line.account_id.display_name))

        sorted_lines = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id, line.amount_currency))

        # ==== Collect all involved lines through the existing reconciliation ====
        involved_lines = sorted_lines
        involved_partials = self.env['account.partial.reconcile']
        current_lines = involved_lines
        current_partials = involved_partials
        while current_lines:
            current_partials = (current_lines.matched_debit_ids + current_lines.matched_credit_ids) - current_partials
            involved_partials += current_partials
            current_lines = (current_partials.debit_move_id + current_partials.credit_move_id) - current_lines
            involved_lines += current_lines

        # ==== Create partials ====

        partials = self.env['account.partial.reconcile'].create(sorted_lines._prepare_reconciliation_partials())

        # Track newly created partials.
        results['partials'] = partials
        involved_partials += partials

        # ==== Create entries for cash basis taxes ====

        is_cash_basis_needed = account.company_id.tax_exigibility and account.user_type_id.type in ('receivable', 'payable')
        if is_cash_basis_needed and not self._context.get('move_reverse_cancel'):
            tax_cash_basis_moves = partials._create_tax_cash_basis_moves()
            results['tax_cash_basis_moves'] = tax_cash_basis_moves

        # ==== Check if a full reconcile is needed ====

        if involved_lines[0].currency_id and all(line.currency_id == involved_lines[0].currency_id for line in involved_lines):
            is_full_needed = all(line.currency_id.is_zero(line.amount_residual_currency) for line in involved_lines)
        else:
            is_full_needed = all(line.company_currency_id.is_zero(line.amount_residual) for line in involved_lines)

        if is_full_needed:

            # ==== Create the exchange difference move ====

            if self._context.get('no_exchange_difference'):
                exchange_move = None
            else:
                exchange_move = involved_lines._create_exchange_difference_move()
                if exchange_move:
                    exchange_move_lines = exchange_move.line_ids.filtered(lambda line: line.account_id == account)

                    # Track newly created lines.
                    involved_lines += exchange_move_lines

                    # Track newly created partials.
                    exchange_diff_partials = exchange_move_lines.matched_debit_ids \
                                             + exchange_move_lines.matched_credit_ids
                    involved_partials += exchange_diff_partials
                    results['partials'] += exchange_diff_partials

                    exchange_move._post(soft=False)

            # ==== Create the full reconcile ====

            results['full_reconcile'] = self.env['account.full.reconcile'].create({
                'exchange_move_id': exchange_move and exchange_move.id,
                'partial_reconcile_ids': [(6, 0, involved_partials.ids)],
                'reconciled_line_ids': [(6, 0, involved_lines.ids)],
            })

        # Trigger action for paid invoices
        not_paid_invoices\
            .filtered(lambda move: move.payment_state in ('paid', 'in_payment'))\
            .action_invoice_paid()

        return results
    
class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'
    
    #If payment matching button only show in posted and CTR status in payment table
    @api.model
    def get_data_for_manual_reconciliation(self, res_type, res_ids=None, account_type=None):
        """ Returns the data required for the invoices & payments matching of partners/accounts (list of dicts).
            If no res_ids is passed, returns data for all partners/accounts that can be reconciled.

            :param res_type: either 'partner' or 'account'
            :param res_ids: ids of the partners/accounts to reconcile, use None to fetch data indiscriminately
                of the id, use [] to prevent from fetching any data at all.
            :param account_type: if a partner is both customer and vendor, you can use 'payable' to reconcile
                the vendor-related journal entries and 'receivable' for the customer-related entries.
        """

        Account = self.env['account.account']
        Partner = self.env['res.partner']

        if res_ids is not None and len(res_ids) == 0:
            # Note : this short-circuiting is better for performances, but also required
            # since postgresql doesn't implement empty list (so 'AND id in ()' is useless)
            return []
        res_ids = res_ids and tuple(res_ids)

        assert res_type in ('partner', 'account')
        assert account_type in ('payable', 'receivable', None)
        is_partner = res_type == 'partner'
        res_alias = is_partner and 'p' or 'a'
        aml_ids = self._context.get('active_ids') and self._context.get('active_model') == 'account.move.line' and tuple(self._context.get('active_ids'))
        all_entries = self._context.get('all_entries', False)
        all_entries_query = """
            AND EXISTS (
                SELECT NULL
                FROM account_move_line l
                JOIN account_move move ON l.move_id = move.id
                JOIN account_journal journal ON l.journal_id = journal.id
                WHERE l.account_id = a.id
                {inner_where}
                AND l.amount_residual != 0
                AND move.state in ('ctr_receipt','posted')
            )
        """.format(inner_where=is_partner and 'AND l.partner_id = p.id' or ' ')
        only_dual_entries_query = """
            AND EXISTS (
                SELECT NULL
                FROM account_move_line l
                JOIN account_move move ON l.move_id = move.id
                JOIN account_journal journal ON l.journal_id = journal.id
                WHERE l.account_id = a.id
                {inner_where}
                AND l.amount_residual > 0
                AND move.state in ('ctr_receipt','posted')
            )
            AND EXISTS (
                SELECT NULL
                FROM account_move_line l
                JOIN account_move move ON l.move_id = move.id
                JOIN account_journal journal ON l.journal_id = journal.id
                WHERE l.account_id = a.id
                {inner_where}
                AND l.amount_residual < 0
                AND move.state in ('ctr_receipt','posted')
            )
        """.format(inner_where=is_partner and 'AND l.partner_id = p.id' or ' ')
        query = ("""
            SELECT {select} account_id, account_name, account_code, max_date
            FROM (
                    SELECT {inner_select}
                        a.id AS account_id,
                        a.name AS account_name,
                        a.code AS account_code,
                        MAX(l.write_date) AS max_date
                    FROM
                        account_move_line l
                        RIGHT JOIN account_account a ON (a.id = l.account_id)
                        RIGHT JOIN account_account_type at ON (at.id = a.user_type_id)
                        {inner_from}
                    WHERE
                        a.reconcile IS TRUE
                        AND l.full_reconcile_id is NULL
                        {where1}
                        {where2}
                        {where3}
                        AND l.company_id = {company_id}
                        {where4}
                        {where5}
                    GROUP BY {group_by1} a.id, a.name, a.code {group_by2}
                    {order_by}
                ) as s
            {outer_where}
        """.format(
                select=is_partner and "partner_id, partner_name, to_char(last_time_entries_checked, 'YYYY-MM-DD') AS last_time_entries_checked," or ' ',
                inner_select=is_partner and 'p.id AS partner_id, p.name AS partner_name, p.last_time_entries_checked AS last_time_entries_checked,' or ' ',
                inner_from=is_partner and 'RIGHT JOIN res_partner p ON (l.partner_id = p.id)' or ' ',
                where1=is_partner and ' ' or "AND ((at.type <> 'payable' AND at.type <> 'receivable') OR l.partner_id IS NULL)",
                where2=account_type and "AND at.type = %(account_type)s" or '',
                where3=res_ids and 'AND ' + res_alias + '.id in %(res_ids)s' or '',
                company_id=self.env.company.id,
                where4=aml_ids and 'AND l.id IN %(aml_ids)s' or ' ',
                where5=all_entries and all_entries_query or only_dual_entries_query,
                group_by1=is_partner and 'l.partner_id, p.id,' or ' ',
                group_by2=is_partner and ', p.last_time_entries_checked' or ' ',
                order_by=is_partner and 'ORDER BY p.last_time_entries_checked' or 'ORDER BY a.code',
                outer_where=is_partner and 'WHERE (last_time_entries_checked IS NULL OR max_date > last_time_entries_checked)' or ' ',
            ))
        self.env['account.move.line'].flush()
        self.env['account.account'].flush()
        self.env.cr.execute(query, locals())

        # Apply ir_rules by filtering out
        rows = self.env.cr.dictfetchall()
        ids = [x['account_id'] for x in rows]
        allowed_ids = set(Account.browse(ids).ids)
        rows = [row for row in rows if row['account_id'] in allowed_ids]
        if is_partner:
            ids = [x['partner_id'] for x in rows]
            allowed_ids = set(Partner.browse(ids).ids)
            rows = [row for row in rows if row['partner_id'] in allowed_ids]

        # Keep mode for future use in JS
        if res_type == 'account':
            mode = 'accounts'
        else:
            mode = 'customers' if account_type == 'receivable' else 'suppliers'

        # Fetch other data
        for row in rows:
            account = Account.browse(row['account_id'])
            currency = account.currency_id or account.company_id.currency_id
            row['currency_id'] = currency.id
            partner_id = is_partner and row['partner_id'] or None
            rec_prop = aml_ids and self.env['account.move.line'].browse(aml_ids) or self._get_move_line_reconciliation_proposition(account.id, partner_id)
            row['reconciliation_proposition'] = self._prepare_move_lines(rec_prop, target_currency=currency)
            row['mode'] = mode
            row['company_id'] = account.company_id.id

        # Return the partners with a reconciliation proposition first, since they are most likely to
        # be reconciled.
        return [r for r in rows if r['reconciliation_proposition']] + [r for r in rows if not r['reconciliation_proposition']]

    #manual reconciliation action for payment table
    @api.model
    def _domain_move_lines_for_manual_reconciliation(self, account_id, partner_id=False, excluded_ids=None, search_str=''):
        """ Create domain criteria that are relevant to manual reconciliation. """
        domain = ['&', '&', ('reconciled', '=', False), ('account_id', '=', account_id), ('move_id.state', 'in', ['ctr_receipt','posted'])]
        if partner_id:
            domain = expression.AND([domain, [('partner_id', '=', partner_id)]])
        if excluded_ids:
            domain = expression.AND([[('id', 'not in', excluded_ids)], domain])
        if search_str:
            str_domain = self._get_search_domain(search_str=search_str)
            domain = expression.AND([domain, str_domain])
        # filter on account.move.line having the same company as the given account
        account = self.env['account.account'].browse(account_id)
        domain = expression.AND([domain, [('company_id', '=', account.company_id.id)]])
        return domain