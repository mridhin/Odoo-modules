# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Import from python lib
import base64
from datetime import datetime
# import from odoo
from odoo import models, fields, _


class eJournalReport(models.Model):
    _name = 'pos_ejournal.report'
    _description = 'POS eJournal Report'

    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    # Added Terminal and MIN in columns
    config_id = fields.Many2one('pos.config', string="Terminal", required=True)
    taxpayer_min = fields.Char(string="MIN", related='config_id.taxpayer_min',
                               store=True)
    transaction_type = fields.Selection([('all', 'All Transaction'),
                                         ('voided', 'Voided'),
                                         ('not_voided', 'Not Voided')],
                                        string='Transaction Type',
                                        default='all',
                                        required=True)
    user_id = fields.Many2one('res.users', string='Cashier',
                              default=lambda self: self.env.uid,
                              )
    partner_id = fields.Many2one('res.partner', string='Customer Name',
                                 index=False, copy=False)

    def get_x_reading_datas(self):
        " Get x reading values"
        x_reading = self.env['cc_x_reading.x_reading'].sudo().search([
                                            ('session_id.config_id', '=', self.config_id.id)],
                                            order='id desc')
        # get X reading values
        x_reading_data = self.get_X_Z_reading_datas(x_reading)

        return x_reading_data

    def get_z_reading_datas(self):
        " Get z reading values"
        z_reading = self.env['cc_z_reading.z_reading'].sudo().search([
                                            ('session_id.config_id', '=', self.config_id.id)],
                                            order='id desc')
        # get Z reading values
        z_reading_data = self.get_X_Z_reading_datas(z_reading)

        return z_reading_data

    def get_X_Z_reading_datas(self, x_z_reading):
        " Get respective X and Z reading values "
        x_z_reading_data = []
        if x_z_reading:
            for x in x_z_reading:
                cashier_ids = []
                payments = []
                if x.payments_ids:
                    self.env.cr.execute("""
                        SELECT method.name, sum(amount) total
                        FROM pos_payment AS payment,
                            pos_payment_method AS method
                        WHERE payment.payment_method_id = method.id
                            AND payment.id IN %s
                        GROUP BY method.name
                    """, (tuple(x.payments_ids.ids),))
                    payments = self.env.cr.dictfetchall()
                for cashier in x.cashier_ids:
                    cashier_ids.append({'name': cashier.name})
                x_z_reading_data.append({
                         'start_date': x.start_date,
                         'end_date': x.end_date,
                         'cashier_ids': cashier_ids,
                         'reference': x.reference,
                         'beginning_reading': x.beginning_reading,
                         'ending_reading': x.ending_reading,
                         'begin_or_no': x.begin_or_no,
                         'end_or_no': x.end_or_no,
                         'acc_beginning': x.acc_beginning,
                         'acc_end': x.acc_end,
                         'acc_beginning_no': x.acc_beginning_no,
                         'acc_end_no': x.acc_end_no,
                         'total_sales': x.total_sales,
                         'total_voids': x.total_voids,
                         'total_discounts': x.total_discounts,
                         'subtotal': x.subtotal,
                         'vatable_sales': x.vatable_sales,
                         'vat_12': x.vat_12,
                         'vat_exempt_sales': x.vat_exempt_sales,
                         'zero_rated_sales': x.zero_rated_sales,
                         'register_total': x.register_total,
                         'payments': payments,
                         'regular_discount': x.regular_discount if x.regular_discount else 0.00,
                         'sc_pwd_vat_in': x.sc_pwd_vat_in if x.sc_pwd_vat_in else 0.00,
                         'sc_vat_ex': x.sc_vat_ex if x.sc_vat_ex else 0.00,
                         'pwd_vat_ex': x.pwd_vat_ex if x.pwd_vat_ex else 0.00,
                         'awb_pos_provider_ptu': x.awb_pos_provider_ptu,
                         'taxpayer_min': x.taxpayer_min,
                         'taxpayer_machine_serial_number': x.taxpayer_machine_serial_number
                         })
        return x_z_reading_data

    def get_order_datas(self):
        """ Get order details based selected param's"""
        data = {}
        domain = [
                  ('session_id.config_id', '=', self.config_id.id),
                  ('user_id', '=', self.user_id.id),
                  ]
        # Filter for selected partner
        if self.start_date:
            start_date_domain = ('date_order', '>=', self.start_date)
            domain.append(start_date_domain)
        if self.end_date:
            end_date_domain = ('date_order', '<=', self.end_date)
            domain.append(end_date_domain)
        if self.partner_id:
            partner_domain = ('partner_id', '=', self.partner_id.id)
            domain.append(partner_domain)

        # Get Order based on selected param's
        pos_orders = self.env['pos.order'].sudo().search(domain, order='date_order desc, id desc')
        # If transaction is voided get refunded orders
        if self.transaction_type == 'voided':
            pos_orders = pos_orders.filtered(lambda order: order.refunded_order_ids)
        elif self.transaction_type == 'not_voided':
            pos_orders = pos_orders.filtered(lambda order: not order.refunded_order_ids)
        if pos_orders:
            order_details = []
            for order in pos_orders:
                config = order.session_id.config_id
                order_type = False
                crm_team_id = config.crm_team_id
                vatable_sales = 0
                vat_amount = 0
                zero_rated = 0
                vat_exempt = 0
                change_amount = 0
                sales_total = 0
                lines = []
                payments = []
                subtotal = 0
                senior_citizen_pwd_total_with_vat = 0
                senior_citizen_pwd_total_without_vat = 0
                senior_citizen_pwd_total = 0
                senior_citizen_disc = 0
                pwd_citizen_disc = 0
                solo_parent_disc = 0

                # accessing the year attribute
                first_date_yr = datetime.now().year
                valid_until = order.company_id.awb_pos_provider_display_valid_until
                valid_date = datetime.strptime(valid_until, '%m/%d/%Y')
                sec_date_yr = valid_date.strftime('%Y')
                total_year = int(sec_date_yr) - int(first_date_yr)
                # Check order has refund ids
                if order.refunded_order_ids:
                    order_type = 'voided'
                for line in order.lines:
                    vatable_sales += line.vatable_sales
                    vat_amount += line.vat_amount
                    zero_rated += line.zero_rated_sales
                    vat_exempt += line.vat_exempt_sales
                    subtotal = (line.qty * line.price_unit)
                    senior_citizen_pwd_total += line.price_unit
                    if line.is_vat_exclusive:
                        senior_citizen_pwd_total_with_vat += line.price_unit
                        senior_citizen_pwd_total_without_vat += line.price_subtotal
                        senior_citizen_disc += round(line.sc_discount_amount,2)
                        pwd_citizen_disc += round(line.pwd_discount_amount,2)
                        solo_parent_disc += round(line.sp_discount_amount,2)

                    lines.append({'name': line.full_product_name,
                                  'qty': line.qty,
                                  'price': line.price_unit,
                                  'discount': line.discount,
                                  'sc_discount': line.sc_discount,
                                  'sc_discount_amount': line.sc_discount_amount,
                                  'pwd_discount': line.pwd_discount,
                                  'pwd_discount_amount': line.pwd_discount_amount,
                                  'sp_discount': line.sp_discount,
                                  'sp_discount_amount': line.sp_discount_amount,
                                  'regular_discount': line.discount,
                                  'discount_value': line.discount,
                                  'pricelist_discount_amount': line.pricelist_discount_amount,
                                  'is_vat_exclusive': line.is_vat_exclusive,
                                  'subtotal': round(subtotal, 2)
                                  })
                senior_citizen_pwd_vat = round(senior_citizen_pwd_total_with_vat - senior_citizen_pwd_total_without_vat, 2)
                senior_citizen_pwd_without_vat = round((senior_citizen_pwd_total - senior_citizen_pwd_vat), 2)
                sales_total = round(vatable_sales + vat_amount + zero_rated + vat_exempt, 2)
                for pay in order.payment_ids:
                    if pay.is_change:
                        change_amount += pay.amount
                    if not pay.is_change:
                        payments.append({'name': pay.payment_method_id.name,
                                         'amount': round(pay.amount, 2),
                                         })
                # update order details
                order_details.append({
                                     'order_date': order.date_order,
                                     'receipt_number': order.pos_reference,
                                     'cashier': order.user_id.name,
                                     'lines': lines,
                                     'payment_lines': payments,
                                     'change_amount': abs(change_amount),
                                     'senior_citizen_pwd_total_with_vat': senior_citizen_pwd_total_with_vat,
                                     'senior_citizen_pwd_total_without_vat': senior_citizen_pwd_total_without_vat,
                                     'senior_citizen_pwd_vat': senior_citizen_pwd_vat,
                                     'senior_citizen_pwd_without_vat': senior_citizen_pwd_without_vat,
                                     'senior_citizen_disc': senior_citizen_disc,
                                     'pwd_citizen_disc': pwd_citizen_disc,
                                     'solo_parent_disc': solo_parent_disc,
                                     'senior_citizen_pwd_total': senior_citizen_pwd_total,
                                     'vatable_sales': vatable_sales,
                                     'vat_amount': vat_amount,
                                     'vat_exempt': order.vat_exempt,
                                     'zero_rated': zero_rated,
                                     'taxpayer_min': config.taxpayer_min,
                                     'taxpayer_serial_number': config.taxpayer_machine_serial_number,
                                     'awb_pos_provider_ptu': config.awb_pos_provider_ptu,
                                     'awb_pos_provider_remarks': crm_team_id.awb_pos_provider_remarks,
                                     'sale_team_prefix': crm_team_id.sale_team_prefix_id.name,
                                     'amount_total': order.amount_total,
                                     'sales_total': sales_total,
                                     'transaction_type': self.transaction_type,
                                     'order_state': order.state,
                                     'order_type': order_type,
                                     'buyer_name': order.partner_id.name if order.partner_id else False,
                                     'street': order.partner_id.street if order.partner_id else False,
                                     'street2': order.partner_id.street2 if order.partner_id else False,
                                     'city': order.partner_id.city if order.partner_id else False,
                                     'state': order.partner_id.state_id.name if order.partner_id and order.partner_id.state_id else False,
                                     'zip': order.partner_id.zip if order.partner_id else False,
                                     'country': order.partner_id.country_id.name if order.partner_id and order.partner_id.country_id else False,
                                     'sc_id': order.partner_id.sc_id if order.partner_id else '',
                                     'pwd_id': order.partner_id.pwd_id if order.partner_id else '',
                                     'sc_pwd': order.partner_id.check_sc_pwd if order.partner_id else '',
                                     'tin': order.partner_id.vat if order.partner_id else '',
                                     'bus_style': order.partner_id.bus_style if order.partner_id else '',
                                     'total_year': total_year
                                     })
            data['order_details'] = order_details
            data['company'] = self.env.company
            # get x reading values
            x_reading_data = self.get_x_reading_datas()
            data['x_reading'] = x_reading_data
            # get z reading values
            z_reading_data = self.get_z_reading_datas()
            data['z_reading'] = z_reading_data
        return data

    def generate_text_report(self):
        """ Generate all the receipts, x reading and z reading filtered by the parameters above
            Only add a line as divider between receipts """
        # get data
        data = self.get_order_datas()
        if data:
            # get report and update in attachments
            report_data = self.env.ref('awb_ejournal_report.action_ejournal_text_report').with_context(data=data)._render_qweb_text(self.id, data=data)
            current_time = datetime.now()
            filename = 'e-Journal-'+str(current_time.year)+str(current_time.month)+str(current_time.day)+'-'
            if self.config_id:
                filename += str(self.config_id.name)+'.txt'
            # create attachment
            ejournal_attachment = self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(report_data[0]),
                'res_model': 'pos_ejournal.report',
                'res_id': self.id,
                'mimetype': 'application/x-txt'
            })
            # get report action
            action = self.env.ref('awb_ejournal_report.action_ejournal_text_report').report_action([], data=data)
            action.update({'close_on_report_download': True})
            return action
        else:
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'ejournal',
                    'message': _("No records found for given params"),
                    'type': 'warning',
                    'sticky': False,  #True/False will display for few seconds if false
                }
                }
            return notification
