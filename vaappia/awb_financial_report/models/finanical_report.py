# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class InheritedReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"
    
    #updated domain values for profit and loss report
    def domain_update(self):
        lines = self.env['account.financial.html.report.line'].sudo().search([])
        for i in lines:
            #Added formulas for all the child lines
            if (i.name == 'Cost of Sales'):
                i.domain = "[('account_id.user_type_id', '=',17)]" 
                i.formulas = 'sum'
                if i.children_ids:
                    for child in i.children_ids:
                        child.formulas = 'sum'
            if (i.name == 'Net Sales'):
                i.domain = "[('account_id.user_type_id', '=',13)]" 
                i.formulas = '-sum'
                if i.children_ids:
                    for child in i.children_ids:
                        child.formulas = '-sum'
            if (i.name == 'Expenses'):
                i.domain = "[('account_id.user_type_id', '=',15)]" 
                i.formulas = 'sum'
                if i.children_ids:
                    for child in i.children_ids:
                        child.formulas = 'sum'
            if (i.name == 'Depreciation'):
                i.domain = "[('account_id.user_type_id', '=',16)]" 
                i.formulas = 'sum'
                if i.children_ids:
                    for child in i.children_ids:
                        child.formulas = 'sum'
            if (i.name == 'Other Income'):
                i.domain = "[('account_id.user_type_id', '=',14)]" 
                i.formulas = '-sum'
                if i.children_ids:
                    for child in i.children_ids:
                        child.formulas = '-sum'
            if (i.name == 'Other Expenses'):
                i.domain = "[('account_id.user_type_id', '=',25)]" 
                i.formulas = 'sum'
                if i.children_ids:
                    for child in i.children_ids:
                        child.formulas = 'sum'
        
    #Added Child lines
    @api.model
    def _build_lines_hierarchy(self, options_list, financial_lines, solver, groupby_keys):
       
        ''' Travel the whole hierarchy and create the report lines to be rendered.
        :param options_list:        The report options list, first one being the current dates range, others being the
                                    comparisons.
        :param financial_lines:     An account.financial.html.report.line recordset.
        :param solver:              The FormulaSolver instance used to compute the formulas.
        :param groupby_keys:        The sorted encountered keys in the solver.
        :return:                    The lines.
        '''
        lines = []
        for financial_line in financial_lines:

            is_leaf = solver.is_leaf(financial_line)
            has_lines = solver.has_move_lines(financial_line)

            financial_report_line = self._get_financial_line_report_line(
                options_list[0],
                financial_line,
                solver,
                groupby_keys,
            )

            # Manage 'hide_if_zero' field with formulas.
            are_all_columns_zero = all(self.env.company.currency_id.is_zero(column['no_format'])
                                       for column in financial_report_line['columns'] if 'no_format' in column)
            if financial_line.hide_if_zero and are_all_columns_zero and financial_line.formulas:
                continue

            # Manage 'hide_if_empty' field.
            if financial_line.hide_if_empty and is_leaf and not has_lines:
                continue
            aml_lines = []
            children = []
            
            if financial_line.children_ids:
                # Travel children.
                children += self._build_lines_hierarchy(options_list, financial_line.children_ids, solver, groupby_keys)
            elif is_leaf and financial_report_line['unfolded']:
                # Fetch the account.move.lines.
                solver_results = solver.get_results(financial_line)
                sign = solver_results['amls']['sign']
                operator = solver_results['amls']['operator']
                for groupby_id, display_name, results in financial_line._compute_amls_results(options_list, self, sign=sign, operator=operator):
                    aml_lines.append(self._get_financial_aml_report_line(
                        options_list[0],
                        financial_report_line['id'],
                        financial_line,
                        groupby_id,
                        display_name,
                        results,
                        groupby_keys,
                    ))
            report_name = self._get_report_name()
#             if 'Balance Sheet' in report_name:
#                 #Created Child lines Blance Sheet Report
#                 #if (financial_line.name == 'Bank and Cash Accounts') or (financial_line.code == 'REC') or (financial_line.code == 'CAS') or (financial_line.name == 'Prepayments') or (financial_line.name == 'Plus Fixed Assets') or (financial_line.code == 'CL1') or (financial_line.code == 'CL2') or (financial_line.name == 'Plus Non-current Assets') or (financial_line.name == 'Retained Earnings') or (financial_line.name == 'OFF BALANCE SHEET ACCOUNTS') or (financial_line.name == 'Plus Non-current Liabilities'):
#                 if (financial_line.groupby == 'analytic_account_id') :    
#                     finan_lines = str(financial_line.domain)
#                     val = finan_lines[1:-1]
#                     analytic_ids = []
#                     if financial_line.children_ids:
#                         a_name = []
#                         for rec in financial_line.children_ids:
#                             #Removed Child lines code in Balance Sheet report
#                             split_code = (rec.name).split(']')
#                             if len(split_code) > 1 :
#                                 a_name.append(split_code[1].strip())
#                                 child_name = split_code[1].strip()
#                             else:
#                                 child_name = rec.name
#                                 a_name.append(rec.name)
#                             rec.name = child_name
#                         
#                         analytic_account_id = self.env['account.analytic.account'].search([('name','in',a_name)])
#                         for analytic in analytic_account_id:
#                             analytic_ids.append(analytic.id)
#                         
#                         analytic_account = self.env['account.analytic.account'].search([('name','not in',a_name)])
#                         for i in analytic_account:
#                             self.env['account.financial.html.report.line'].sudo().create({'name':i.name,
#                                                                 'sequence':3,
#                                                                 'level':4,
#                                                                  'parent_id':financial_line.id,
#                                                                  'formulas':'sum',
#                                                                  'groupby':'account_id',
#                                                                  'domain':"[('analytic_account_id.name', '=', '"+i.name+"'),"+str(val)+"]",
#                                                                 })
#                     else:
#                         #Created Child lines
#                         if (financial_line.groupby and financial_line.domain) :
#                             analytic_account = self.env['account.analytic.account'].search([])
#                             for i in analytic_account:
#                                 financial_line.children_ids.create({'name':i.name,
#                                                                     'sequence':3,
#                                                                     'level':4,
#                                                                     'formulas':'sum',
#                                                                      'parent_id':financial_line.id,
#                                                                      'groupby':'account_id',
#                                                                      'domain':"[('analytic_account_id.name', '=', '"+i.name+"'),"+str(val)+"]",
#                                                                     })
#                     financial_line.groupby = 'analytic_account_id'
#                     if analytic_ids:
#                         children_ids = "["+val+","+"('analytic_account_id','in',"+str(analytic_ids)+")]"
#                     else:
#                         children_ids = financial_line.domain
#                     financial_line.domain = children_ids
            if 'Profit and Loss' in report_name:
                #Created Child lines for profit and loss 
                if ((financial_line.name == 'Operating Income') or (financial_line.name == 'Cost of Revenue') or (financial_line.name == 'Other Income') or (financial_line.code == 'EXP')  or (financial_line.name == 'Depreciation') or (financial_line.name == 'Net Sales') or (financial_line.name == 'Cost of Sales') or (financial_line.groupby == 'analytic_account_id')) and (financial_line.name != 'Undefined'):
                    finan_lines = str(financial_line.domain)
                    val = finan_lines[1:-1]
                    #Removed Child lines code in profit and loss report
                    if financial_line.children_ids:
                        a_name = []
                        undefined_val=[]
                        for rec in financial_line.children_ids:
                            undefined_val.append(rec.name)
                            a_name.append(rec.name)
                            rec.name = rec.name
                        account_move_line = self.env['account.move.line'].search([])
                        move_id = []
                        #If analytic account is archived, do not show in report.
                        for line in account_move_line:
                            if line.analytic_account_id.name != False:
                                move_id.append(line.analytic_account_id.name)
                        list_act_name = list(set(move_id))
                        for lines_name in financial_line.children_ids:
                            if lines_name.name not in list_act_name:
                                if lines_name.name != 'Undefined':
                                    lines_name.unlink()
                        line_ids = []
                        for lines_ids in financial_line.children_ids:
                            line_ids.append(lines_ids.name)
                        for move_ids in list_act_name:
                            if move_ids not in line_ids:
                                self.env['account.financial.html.report.line'].sudo().create({'name':move_ids,
                                                                'sequence':3,
                                                                'level':4,
                                                                 'parent_id':financial_line.id,
                                                                 'formulas':financial_line.formulas,
                                                                 'groupby':'account_id',
                                                                 'domain':"[('analytic_account_id.name', '=', '"+move_ids+"'),"+str(val)+"]",
                                                                })
                        #Created Undefined lines
                        if 'Undefined' not in undefined_val:
                            undefined_name = "["+str(val)+",('analytic_account_id','=',False)]"
                            financial_line.children_ids.create({'name':'Undefined',
                                                        'sequence':3,
                                                        'level':4,
                                                        'formulas':financial_line.formulas,
                                                        'parent_id':financial_line.id,
                                                        'groupby':'analytic_account_id',
                                                        'domain':str(undefined_name),
                                                        }) 
                    else:
                        #Created Child lines
                        if (financial_line.groupby and financial_line.domain) :
                            analytic_account = self.env['account.analytic.account'].search([])
                            analytic_act_id = []
                            for i in analytic_account:
                                analytic_act_id.append(i.id)
                            account_move_line = self.env['account.move.line'].search([])
                            move_id = []
                            for line in account_move_line:
                                if line.analytic_account_id.name != False:
                                    move_id.append(line.analytic_account_id.name)
                            list_move_id = list(set(move_id))
                            for act_id in list_move_id:
                                financial_line.children_ids.create({'name':act_id,
                                                                    'sequence':3,
                                                                    'level':4,
                                                                    'formulas':financial_line.formulas,
                                                                    'parent_id':financial_line.id,
                                                                    'groupby':'account_id',
                                                                    'domain':"[('analytic_account_id.name', '=', '"+act_id+"'),"+str(val)+"]",
                                                                    })
                             
                            
            # Manage 'hide_if_zero' field without formulas.
            # If a line hi 'hide_if_zero' and has no formulas, we have to check the sum of all the columns from its children
            # If all sums are zero, we hide the line
            if financial_line.hide_if_zero and not financial_line.formulas:
                amounts_by_line = [[col['no_format'] for col in child['columns'] if 'no_format' in col] for child in children]
                amounts_by_column = zip(*amounts_by_line)
                all_columns_have_children_zero = all(self.env.company.currency_id.is_zero(sum(col)) for col in amounts_by_column)
                if all_columns_have_children_zero:
                    continue
            lines.append(financial_report_line)
            lines += children
            lines += aml_lines

            if self.env.company.totals_below_sections and (financial_line.children_ids or (is_leaf and financial_report_line['unfolded'] and aml_lines)):
                lines.append(self._get_financial_total_section_report_line(options_list[0], financial_report_line))
                financial_report_line["unfolded"] = True  # enables adding "o_js_account_report_parent_row_unfolded" -> hides total amount in head line as it is displayed later in total line

        return lines
    #Added Parent id for all the child lines
    @api.model
    def _get_financial_line_report_line(self, options, financial_line, solver, groupby_keys):
        ''' Create the report line for an account.financial.html.report.line record.
        :param options:             The report options.
        :param financial_line:      An account.financial.html.report.line record.
        :param solver_results:      An instance of the FormulaSolver class.
        :param groupby_keys:        The sorted encountered keys in the solver.
        :return:                    The dictionary corresponding to a line to be rendered.
        '''
        results = solver.get_results(financial_line)['formula']
        is_leaf = solver.is_leaf(financial_line)
        has_lines = solver.has_move_lines(financial_line)
        has_something_to_unfold = is_leaf and has_lines and bool(financial_line.groupby)
 
        # Compute if the line is unfoldable or not.
        is_unfoldable = has_something_to_unfold and financial_line.show_domain == 'foldable'
 
        # Compute the id of the report line we'll generate
        report_line_id = self._get_generic_line_id('account.financial.html.report.line', financial_line.id)
 
        # Compute if the line is unfolded or not.
        # /!\ Take care about the case when the line is unfolded but not unfoldable with show_domain == 'always'.
        if not has_something_to_unfold or financial_line.show_domain == 'never':
            is_unfolded = False
        elif financial_line.show_domain == 'always':
            is_unfolded = True
        elif financial_line.show_domain == 'foldable' and (report_line_id in options['unfolded_lines'] or options.get('unfold_all')):
            is_unfolded = True
        else:
            is_unfolded = False
 
        # Standard columns.
        columns = []
        for key in groupby_keys:
            amount = results.get(key, 0.0)
            columns.append({'name': self._format_cell_value(financial_line, amount), 'no_format': amount, 'class': 'number'})
 
        # Growth comparison column.
        if self._display_growth_comparison(options):
            columns.append(self._compute_growth_comparison_column(options,
                columns[0]['no_format'],
                columns[1]['no_format'],
                green_on_positive=financial_line.green_on_positive
            ))
        financial_report_line = {
        'id': report_line_id,
        'name': financial_line.name,
        'model_ref': ('account.financial.html.report.line', financial_line.id),
        'level': financial_line.level,
        'class': 'o_account_reports_totals_below_sections' if self.env.company.totals_below_sections else '',
        'columns': columns,
        'unfoldable': is_unfoldable,
        'unfolded': is_unfolded,
        'page_break': financial_line.print_on_new_page,
        'action_id': financial_line.action_id.id,
        }
        report_name = self._get_report_name()
        #If only show selected analytic accounts name
        if 'Profit and Loss' in report_name: 
            if financial_line:
                id = financial_line.parent_id.id
                financial_report_line['parent_id'] = '-account.financial.html.report.line-'+str(id)
                options_lines = options.get('selected_analytic_account_names')
                if (financial_line.name != 'Operating Income') and (financial_line.name != 'Cost of Revenue') and (financial_line.name != 'Gross Profit') and (financial_line.name != 'Other Income') and (financial_line.name != 'Depreciation'):
                    if (financial_line.domain != False):
                        if options_lines:
                            split_code = (financial_line.name).split(']')
                            if len(split_code) > 1 :
                                finance_line_name = split_code[1].strip()
                            else:
                                finance_line_name = financial_line.name
                            if finance_line_name in options_lines:
                                financial_report_line['style'] = 'color:black'
                            else:
                                financial_report_line['style'] = 'display:none'
#         if 'Balance Sheet' in report_name: 
#             if financial_line:
#                 id = financial_line.parent_id.id
#                 financial_report_line['parent_id'] = '-account.financial.html.report.line-'+str(id)
#                 options_lines = options.get('selected_analytic_account_names')
#                 if (financial_line.name != 'Bank and Cash Accounts') and (financial_line.code != 'REC') and (financial_line.name != 'Prepayments') and (financial_line.name != 'Plus Fixed Assets') and (financial_line.name != 'Plus Non-current Assets') and (financial_line.name != 'Plus Non-current Assets') and (financial_line.code != 'CL2') and (financial_line.name != 'Plus Non-current Liabilities') and (financial_line.name != 'Retained Earnings'):
#                     if (financial_line.domain != False):
#                         if options_lines:
#                             split_code = (financial_line.name).split(']')
#                             if len(split_code) > 1 :
#                                 finance_line_name = split_code[1].strip()
#                             else:
#                                 finance_line_name = financial_line.name
#                             if finance_line_name in options_lines:
#                                 financial_report_line['style'] = 'color:black'
#                             else:
#                                 financial_report_line['style'] = 'display:none'
                
        # Only run the checks in debug mode
        if self.user_has_groups('base.group_no_one'):
            # If a financial line has a control domain, a check is made to detect any potential discrepancy
            if financial_line.control_domain:
                if not financial_line._check_control_domain(options, results, self):
                    # If a discrepancy is found, a check is made to see if the current line is
                    # missing items or has items appearing more than once.
                    has_missing = solver._has_missing_control_domain(options, financial_line)
                    has_excess = solver._has_excess_control_domain(options, financial_line)
                    financial_report_line['has_missing'] = has_missing
                    financial_report_line['has_excess'] = has_excess
                    # In either case, the line is colored in red.
                    # The ids of the missing / excess report lines are stored in the options for the top yellow banner
                    if has_missing:
                        financial_report_line['class'] += ' alert alert-danger'
                        options.setdefault('control_domain_missing_ids', [])
                        options['control_domain_missing_ids'].append(financial_line.id)
                    if has_excess:
                        financial_report_line['class'] += ' alert alert-danger'
                        options.setdefault('control_domain_excess_ids', [])
                        options['control_domain_excess_ids'].append(financial_line.id)
 
        # Debug info columns.
        if self._display_debug_info(options):
            columns.append(self._compute_debug_info_column(options, solver, financial_line))
 
        # Custom caret_options for tax report.
        if self.tax_report and financial_line.domain and not financial_line.action_id:
            financial_report_line['caret_options'] = 'tax.report.line'
             
        return financial_report_line
    
     
