from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    """
        TODO: Consider storing the values.
    """
    amount_vatable_sales = fields.Monetary(string='VATable Sales', compute='_compute_breakdown', store=True)
    amount_vat_amount = fields.Monetary(string='VAT Amount', compute='_compute_breakdown', store=True)
    amount_vat_exempt_sales = fields.Monetary(string='VAT Exempt Sales', compute='_compute_breakdown', store=True)
    amount_zero_rated_sales = fields.Monetary(string='Zero-Rated Sales', compute='_compute_breakdown', store=True)
    amount_total_discounts = fields.Monetary(string='Total Discounts', compute='_compute_breakdown', store=True)

    """
        Check if the transaction is tax inclusive or tax exclusive.
    """
    is_tax_exclusive = fields.Boolean(default='False')

    """
        New fields for sc/pwd transactions.
    """
    amount_total_sales_w_vat = fields.Monetary(string='Total Sales (with VAT)', compute='_compute_breakdown', store=True)
    amount_less_vat = fields.Monetary(string='Less: VAT', compute='_compute_breakdown', store=True)
    amount_net_vat = fields.Monetary(string='Amount (net of VAT)', compute='_compute_breakdown', store=True)
    amount_add_vat = fields.Monetary(string='Add: VAT', compute='_compute_breakdown', store=True)
    amount_total_amount = fields.Monetary(string='Total Amount', compute='_compute_breakdown', store=True)

    """
        Counter for number of times the report is printed.
    """
    print_increment = fields.Integer(default=0)


    """
        This function is called when the print button is pressed and _get_report_values
            is called.
    """
    def _print_increment(self):
        self.print_increment += 1

    def _get_price_info(self, price, quantity, product_id, tax_id):
        """
            Passed quantity to this function to prevent decimal inaccuracy later on.

            The function compute_all is from account.tax. For more information regarding
                the function, please refer to the original source code.
            
            The result of the function are for fetching base price information such as:
                {'base_tags': [], 'taxes': [{'id': 82, 'name': '12% VAT (TEST)', 
                'amount': 1554.0, 'base': 12950.0, 'sequence': 1, 'account_id': False, 
                'analytic': False, 'price_include': False, 
                'tax_exigibility': 'on_invoice', 'tax_repartition_line_id': 326, 
                'group': None, 'tag_ids': [], 'tax_ids': []}], 
                'total_excluded': 12950.0, 'total_included': 14504.0, 
                'total_void': 14504.0}

        """
        res = tax_id.compute_all(price, quantity=quantity, product=product_id, partner=self.env['res.partner'])
        return res
    
    """
        TODO: add depends here;

        For now same depends as _compute_all from account.move.
        
    """
    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_breakdown(self):
        for move in self:
            
            move.is_tax_exclusive = False
            is_pricelist = False
            is_promo_coupon = False
            is_product_id = False
            is_discount = False
            total_discounts = 0.0

            total_vatable_sales = 0.0
            total_vatable_sales_currency = 0.0

            total_vat_amount = 0.0
            total_vat_amount_currency = 0.0

            total_vat_exempt_sales = 0.0
            total_vat_exempt_sales_currency = 0.0

            total_zero_rated_sales = 0.0
            total_zero_rated_sales_currency = 0.0
            
            total_sales_w_vat = 0.0
            total_less_vat = 0.0
            total_net_vat = 0.0
            total_add_vat = 0.0

            currencies = move._get_lines_onchange_currency().currency_id

            if move.sale_order_id['pricelist_id']:
                is_pricelist = True

            """
                Changed loop to loop through invoice_line_ids so that it only fetches product data needed
                  for the computations.
            """

            for line in move.invoice_line_ids:
                """
                    This is under the assumption that only one tax is selected.
                        Multiple taxes might cause issues.
                    TODO: Either disable multiple taxes or adjust the computation to
                        cater to it.
                """
                
                tax = line['tax_ids']

                """
                    IF is_pricelist and line['product_id'] >> if pricelist
                    OR line['discount'] and line['product'] >> if discount
                    OR line['sale_line_ids'].is_reward_line >> if promo/coupon

                    for getting price tax included and price tax excluded
                    check if product is present >>> line['sale_line_ids'].product_id or line['product_id']:
                        price_tax_included = line['sale_line_ids'].price_reduce_taxinc 
                        price_tax_excluded = line['sale_line_ids'].price_reduce_taxexcl
                """
                # reset the following variables so it checks per invoice line
                is_product_id = False
                is_discount = False
                is_promo_coupon = False

                if hasattr(line['sale_line_ids'], 'is_reward_line'):
                    if line['sale_line_ids'].is_reward_line:
                        is_promo_coupon = True

                if 'product_id' in line:
                    if line['product_id']:
                        is_product_id = True

                if 'discount' in line:
                    if line['discount']:
                        is_discount = True

                if is_pricelist and is_product_id or is_discount or is_promo_coupon:
                    # ========== PRICELIST & DISCOUNTS ==========
                    product_lst_price = line['product_id'].lst_price
                    price_total = line['price_total']
                    qty = line['quantity']
                    
                    """
                        1. get price tax included but before discounts as list_price
                        2. get compare list_price and price_total
                        3. difference between the two is pricelist_values
                    """
                    base_product_price_info = move._get_price_info(product_lst_price, qty, line['product_id'], tax)
                    base_total = base_product_price_info['total_included']

                    if base_total != price_total and not is_promo_coupon:
                        total_discounts += abs(base_total - price_total)
                    
                    # ========== COUPON & PROGRAM ==========
                    if is_promo_coupon:
                        total_discounts += abs(price_total)
                
                """
                    amount_total_sales_w_vat = base product pricelist with tax
                    amount_vat = base product tax amount
                    amount_net_vat = base product price without tax
                    amount_total_amount = (amount_total_sales_w_vat - amount_vat - discounts + amount_vat)
                """
                # ========== SALES BREAKDOWN ==========
                if line['product_id']:
                    product_lst_price = line['product_id'].lst_price
                    base_tax_id = line['product_id'].taxes_id
                    qty = line['quantity']

                    # If tax applied is changed into vat_exempt
                    if tax != base_tax_id and tax.tax_type == 'vat_exempt':
                        base_product_price_info = move._get_price_info(product_lst_price, qty, line['product_id'], base_tax_id)
                    else:
                        base_product_price_info = move._get_price_info(product_lst_price, qty, line['product_id'], tax)
                    
                    total_sales_w_vat += base_product_price_info['total_included']

                    # Check if taxes are present
                    if base_product_price_info['taxes']:
                        total_less_vat += base_product_price_info['taxes'][0]['amount']

                    total_net_vat += base_product_price_info['total_excluded']


                if tax and line['product_id']:
                    """
                        if invoice line is a product and has taxes
                    """
                    if tax.tax_type == 'vatable':
                        # ========== VATABLE SALES ==========
                        total_vatable_sales += line.balance
                        total_vatable_sales_currency += line.amount_currency
                        
                        """
                            total_add_vat += the tax amount of the base product.
                            meaning the discount is vat inclusive.
                            else add nothing to total_add_vat.
                        
                        """
                        product_lst_price = line['product_id'].lst_price
                        base_product_price_info = move._get_price_info(product_lst_price, qty, line['product_id'], tax)
                        total_add_vat += base_product_price_info['taxes'][0]['amount']
                        
                        # ========== VAT AMOUNT ==========
                        """
                            To compute the VAT Amount:
                            1. get the price_unit after discounts
                            2. pass the variable to _get_price_info
                            3. use the calculated tax amount as total_vat_amount
                        """
                        price_unit_w_qty = line['price_unit'] * line['quantity'] 
                        price_unit_after_disc = price_unit_w_qty - (price_unit_w_qty * (line['discount']/100))
                        vatable_tax = move._get_price_info(price_unit_after_disc, qty, line['product_id'], tax)
                        # Check if blank to prevent errors
                        if vatable_tax['taxes']:
                            total_vat_amount += vatable_tax['taxes'][0]['amount']
                        
                    elif tax.tax_type == 'vat_exempt':
                        # ========== VAT EXEMPT SALES ==========
                        total_vat_exempt_sales += line.balance
                        total_vat_exempt_sales_currency += line.amount_currency
                        """
                            If tax_type is vat_exempt, the transaction is now tax
                                exclusive.
                        """
                        move.is_tax_exclusive = True

                    elif tax.tax_type == 'zero_rated':
                        # ========== ZERO RATED SALES ==========
                        total_zero_rated_sales += line.balance
                        total_zero_rated_sales_currency += line.amount_currency

                """
                    Get sign here
                """
                if move.move_type == 'entry' or move.is_outbound():
                    sign = 1
                else:
                    sign = -1

                move.amount_vatable_sales = sign * (total_vatable_sales_currency if len(currencies) == 1 else total_vatable_sales)
                move.amount_vat_amount = (total_vat_amount if len(currencies) == 1 else total_vat_amount)
                move.amount_vat_exempt_sales = sign * (total_vat_exempt_sales_currency if len(currencies) == 1 else total_vat_exempt_sales)
                move.amount_zero_rated_sales = sign * (total_zero_rated_sales_currency if len(currencies) == 1 else total_zero_rated_sales)
                move.amount_total_discounts = (total_discounts if len(currencies) == 1 else total_discounts)

                move.amount_total_sales_w_vat = (total_sales_w_vat if len(currencies) == 1 else total_sales_w_vat)
                move.amount_less_vat = (total_less_vat if len(currencies) == 1 else total_less_vat)
                move.amount_net_vat = (total_net_vat if len(currencies) == 1 else total_net_vat)
                move.amount_add_vat = (total_add_vat if len(currencies) == 1 else total_add_vat)
            
class ReportInvoiceWithPayment(models.AbstractModel):
    """
        This is inherited for incrementing the print_increment field in
            account.move. The function _get_report_values is called
            everytime a report is being generated. Therefore by calling
            _print_increment everytime a report is being generated, we
            can keep track of how many times the report is generated.

        If print_increment > 1, the report is now a REPRINT.
    """
    _inherit = 'report.account.report_invoice'

    @api.model
    def _get_report_values(self, docids, data=None):
        rslt = super()._get_report_values(docids, data)
        _docs = rslt['docs']
        _docs._print_increment()
        return rslt

