# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Import from python lib
from datetime import datetime
from dateutil.relativedelta import relativedelta

# import from odoo
from odoo import models, fields, _
from odoo.addons.test_testing_utilities.tests.test_form_impl import get
from _datetime import timedelta

# create the new class and model
class SalesBookReport(models.Model):
    _name = 'pos.sale.report'
    _description = 'POS Sale Report'
    
    # Removed unwanted required fields
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    company_name = fields.Many2one('res.company', string='Company Name', 
                                required=True, index=False, copy=False,)
    tin_number = fields.Char(string='TIN number', related='company_name.vat')
    acc_number_pos = fields.Char(string='Accreditation No.', related='company_name.awb_pos_provider_accreditation_no')
    pos_terniman_number = fields.Many2one('pos.config', string='POS terminal number', 
                                required=True, index=False, copy=False)
    min = fields.Char(string='MIN',related='pos_terniman_number.taxpayer_min')
    ptu = fields.Char(string='PTU',related='pos_terniman_number.awb_pos_provider_ptu')
    # user_id = fields.Many2one('res.users', string='Cashier',
    #                           default=lambda self: self.env.uid,
    #                           )
    # partner_id = fields.Many2one('res.partner', string='Customer Name', 
    #                              required=True, index=False, copy=False)
    
    from datetime import datetime

    def generate_report(self):
        # Date order Fixed
        start_date = self.start_date.date().strftime('%Y-%m-%d')
        end_date = self.end_date.date().strftime('%Y-%m-%d')
        date_time = datetime.today()
        user_id = self.env.uid
        user_id_name = self.env['res.users'].search([('id', '=', user_id)])
        previous_date = (self.start_date.date() - relativedelta(days=1)).strftime('%Y-%m-%d')
        select = """
            SELECT min(po.pos_reference) AS min_order, max(po.pos_reference) AS max_order, SUM(po.amount_total) AS amount_total, SUM(pol.vat_amount) AS vat_amount, SUM(pol.vatable_sales) AS vatable_sales,
            SUM(pol.zero_rated_sales) AS zero_rated_sales, SUM(pol.vat_exempt_sales) AS vat_exempt_sales,
            SUM(pol.sc_discount_amount) AS sc_discount_amount, SUM(pol.pwd_discount_amount) AS pwd_discount_amount, cast(po.date_order as date)
            FROM pos_session ps
            INNER JOIN pos_order po ON po.session_id = ps.id
            INNER JOIN pos_order_line pol ON pol.order_id = po.id
            WHERE cast(po.date_order as date) >= %s AND cast(po.date_order as date) <= %s
            GROUP BY cast(po.date_order as date)
        """
        

        
        query_lines = []
        table_values = {}
        header = {}
        symbol ={}
        date_time = {}
        convert_date = self.env['ir.qweb.field.date'].value_to_html
    
        self.env.cr.execute(select, (start_date, end_date))
        results = self.env.cr.fetchall()
    
        # Notification added in case for the wrong entered values
        if not results:
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'BIR POS REPORT (SALES BOOK)',
                    'message': _("No records found for given parameters"),
                    'type': 'warning',
                    'sticky': False,
                }
            }
            return notification
    
        beg_bal = 0.00
        check = False
        for record in results:
            terminal_id = self.pos_terniman_number
            z_reading_id = self.env['cc_z_reading.z_reading'].search([('start_date', '>=', start_date), ('end_date', '<=', end_date),('reference', 'ilike', self.pos_terniman_number.name)], order='start_date asc')   
            for z_read in z_reading_id:
                if z_read:
                    formatted_date_order = z_read.start_date.strftime('%d-%m-%y')
                    total_sale = record[2]
                    query_lines.append({
                        'date_order' : formatted_date_order,
                        'min_order': z_read.begin_or_no,
                        'max_order': z_read.end_or_no,
                        'ending_bal': z_read.ending_reading,
                        'total_sale': z_read.total_sales,
                        'vat_amount': z_read.vat_12,
                        'vatable_sales': z_read.vatable_sales,
                        'zero_rated_sales': z_read.zero_rated_sales,
                        'vat_exempt_sales': z_read.vat_exempt_sales,
                        'sc_discount_amount': z_read.sc_vat_ex,
                        'pwd_discount_amount': z_read.pwd_vat_ex,
                        'date_order': formatted_date_order,
                        'unfoldable': False,
                        'caret_options': 'pos.order',
                        'level': 4,
                        'beg_bal': z_read.beginning_reading,
                    })
            
                    # beg_bal = total_sale
                table_values = query_lines
                domain = [('date_order', '>=', self.start_date),
                          ('date_order', '<=', self.end_date),
                          ]
        
            
                header = {
                    'start_date': self.start_date.date().strftime('%d-%m-%y'),
                    'end_date': self.end_date.date().strftime('%d-%m-%y'),
                    'company_name': self.company_name.name,
                    'tin_number': self.tin_number,
                    'pos_terminal_no': self.pos_terniman_number.name,
                    'min': self.min,
                    'ptu': self.ptu,
                    'acc_number_pos': self.acc_number_pos
                }
            
            data = {
                'query_lines': query_lines,
                'header_details': header,
                'date_time': date_time,
                'company': user_id_name.name,
                # 'symbol':symbol,
            }
            action = self.env.ref('awb_sale_book_report.action_sale_report').report_action([], data=data)
            action.update({'close_on_report_download': True})
            return action
