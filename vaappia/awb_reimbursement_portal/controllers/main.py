# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http, _
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from werkzeug.utils import redirect


class CustomerPortal(portal.CustomerPortal):
    # count for expenses table records
    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        if 'expenses_count' in counters:
            values['expenses_count'] = request.env['hr.expense'].sudo().search_count([
            ])
        return values    
    def _get_searchbar_inputs(self):
        return {
            'all': {'input': 'all', 'label': _('Search in All')},
            'employee': {'input': 'employee', 'label': _('Search in Employee')},
            'project': {'input': 'product', 'label': _('Search in Product')},
        }
        
    @http.route(['/my/expenses', '/my/expenses/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_expenses(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        hr_expenses = request.env['hr.expense'].sudo().search([])
        domain = []
        expenses = request.env['hr.expense']
        expenses_sudo = expenses.sudo()
        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'create_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        expenses_count = expenses_sudo.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/expenses",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=expenses_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        expenses = hr_expenses.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_expenses_history'] = expenses.ids[:100]
        state_expense = request.env['hr.expense'].sudo().search([])
        values.update({
            'date': date_begin,
            'expenses': hr_expenses,
            'state_expenses': state_expense,
            'page_name': 'expenses',
            'pager': pager,
            'default_url': '/my/expenses',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("awb_reimbursement_portal.portal_my_expenses", values)
    
    
    @http.route(['/expense_lines/creation'], type='json', auth="public",
                methods=['POST'], website=True)
    def booking_order_creation(self, **kw):
        """ Display Expenses details creation form.
        @return popup.
        """
        values = {
                  'product': request.env['product.product'].sudo().search([]),
                  'status':kw.get('status'),
                  'description': kw.get('description'),
                  'total': kw.get('total'),
                  'taxes': request.env['account.tax'].sudo().search([]),
                  'bill_reference': kw.get('bill_reference'),
                  'expense_date': kw.get('expense_date'),
                  'account': request.env['account.account'].sudo().search([]),
                  'analytic_account': request.env['account.analytic.account'].sudo().search([]),
                  'analytic_tages': request.env['account.analytic.tag'].sudo().search([]),
                  'employee': request.env['hr.employee'].sudo().search([]),
                  'paid_of_employee': kw.get('paid_of_employee'),
                }

        return request.env['ir.ui.view']._render_template("awb_reimbursement_portal.portal_layout",
                                                         values)
        
    @http.route('/new/row/expense_lines', method='post', type='http', auth='public',
                website=True, csrf=False)
    def new_row_expenselines(self, **post):
        """ Render the New line row template """
        values = {
            'name':post['description'],
            'product_id':1,
            'total_amount': post['total'],
            'tax_ids': [(6, 0, [int(post['taxes'])])] if post['taxes'] else False,
            'reference': post['bill_reference'],
            'date': post['date'],
            'account_id':int(post['account']) if post['account'] else False,
            'analytic_account_id': int(post['analytic_act']) if post['analytic_act'] else False,
            'analytic_tag_ids': [(6, 0, [int(post['analytic_tag'])])] if post['analytic_tag'] else False,
            'employee_id': int(post['employee']) if post['employee'] else False,
            'unit_amount':0.0,
            }
        req = request.env['hr.expense'].sudo().create(values)
        return redirect('/my/expenses')
    
    @http.route('/submit/expenses', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def submit_expesnses(self, **kw):
        """ Render the submit line row template """
        expense_id = kw.get('checked')
        for rec in expense_id:
            if rec:
                expense = request.env['hr.expense'].sudo().search(
                    [('id', '=', int(rec))])
                if expense.state=='draft':
                    expense.update({
                    'state' : 'reported'
                    })
        #filter selected row values            
        values = {
        'expenses':request.env['hr.expense'].sudo().search([('id','in',expense_id)]),
        'paid_by_emp':'True'
        }
        return request.env['ir.ui.view']._render_template(
            "awb_reimbursement_portal.submitted_expense_lines_row", values)
        
    @http.route('/create/expenses/records', methods=['POST'], type='json',
                auth='user', website=True, csrf=False)
    def request(self):
        """ Render the submit line row values """
        hr_expenses = request.env['product.product'].sudo().search([])
        account_tax = request.env['account.tax'].sudo().search([])
        account_account = request.env['account.account'].sudo().search([])
        employee = request.env['hr.employee'].sudo().search([])
        analytic_act = request.env['account.analytic.account'].sudo().search([])
        analytic_tag = request.env['account.analytic.tag'].sudo().search([])
        product_dict = []
        taxes_dict = []
        account_dict = []
        employee_dict = []
        analytic_act_dict = []
        analytic_tag_dict = []
        for rec in hr_expenses:
            product_dict.append({'id': rec.id, 'name': rec.name})
        for account in account_tax:
            taxes_dict.append({'id': account.id, 'name': account.name})
        for act in account_account:
            account_dict.append({'id': act.id, 'name': act.name})
        for emp in employee:
            employee_dict.append({'id': emp.id, 'name': emp.name})
        for analytic in analytic_act:
            analytic_act_dict.append({'id': analytic.id, 'name': analytic.name})
        for tag in analytic_tag:
            analytic_tag_dict.append({'id': tag.id, 'name': tag.name})
        res = {
            'product': product_dict,
            'taxes': taxes_dict,
            'account': account_dict,
            'employee': employee_dict,
            'analytic_act': analytic_act_dict,
            'analytic_tag': analytic_tag_dict,
            
        }
        return res
    