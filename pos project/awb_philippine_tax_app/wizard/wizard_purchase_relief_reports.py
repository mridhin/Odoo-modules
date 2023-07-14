# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta
from io import BytesIO
import xlsxwriter
from operator import itemgetter
from odoo import models, fields, api


class WizardPurchaseReliefReports(models.TransientModel):
    _name = 'wizard.purchase.relief.reports'
    _description = 'Purchase Relief Reports'

    awb_company_id = fields.Many2one('res.company', string='Company')
    awb_fiscal_year = fields.Many2one(
        'account.fiscal.year', string='Fiscal Year')
    awb_fiscal_qua = fields.Many2one(
        'account.month.period', string='Fiscal Quarter')

    # def get_data_for_purchase_relief(self):
    # @api.onchange('awb_fiscal_year')
    def get_data(self):
        start_date = self.awb_fiscal_qua.date_start
        end_date = self.awb_fiscal_qua.date_stop
        company_id = self.awb_company_id
        domain = [
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('company_id', '=', company_id.id)
        ]
        move_obj = self.env['account.move'].search(domain)
        data = []
        data_refund = []
        for move in move_obj:
            if move.move_type == 'in_invoice':
                if move.partner_id not in list(map(itemgetter('partner'), data)):
                    svc_ph = 0
                    z_ph = 0
                    cap_ph = 0
                    ex_ph = 0
                    for invoice_lines in move.invoice_line_ids:
                        if invoice_lines.tax_ids.name in ['EX-PH', 'Z-PH', 'SVC-PH', 'CAP-PH'] and invoice_lines.tax_ids.type_tax_use == 'purchase':
                            if invoice_lines.tax_ids.name == 'SVC-PH':
                                svc_ph = invoice_lines.price_subtotal + svc_ph
                            if invoice_lines.tax_ids.name == 'Z-PH':
                                z_ph = invoice_lines.price_subtotal + z_ph
                            if invoice_lines.tax_ids.name == 'CAP-PH':
                                cap_ph = invoice_lines.price_subtotal + cap_ph
                            if invoice_lines.tax_ids.name == 'EX-PH':
                                ex_ph = invoice_lines.price_subtotal + ex_ph
                    data.append({'partner': move.partner_id, 'svc_ph': svc_ph,
                                 'z_ph': z_ph, 'cap_ph': cap_ph, 'ex_ph': ex_ph})
                else:
                    svc_ph = 0
                    z_ph = 0
                    cap_ph = 0
                    ex_ph = 0
                    for invoice_lines in move.invoice_line_ids:
                        if invoice_lines.tax_ids.name in ['SVC-PH', 'Z-PH', 'CAP-PH', 'EX-PH'] and invoice_lines.tax_ids.type_tax_use == 'purchase':
                            if invoice_lines.tax_ids.name == 'SVC-PH':
                                svc_ph = invoice_lines.price_subtotal + svc_ph
                            if invoice_lines.tax_ids.name == 'Z-PH':
                                z_ph = invoice_lines.price_subtotal + z_ph
                            if invoice_lines.tax_ids.name == 'CAP-PH':
                                cap_ph = invoice_lines.price_subtotal + cap_ph
                            if invoice_lines.tax_ids.name == 'EX-PH':
                                ex_ph = invoice_lines.price_subtotal + ex_ph
                    for i in data:
                        if i['partner'] == move.partner_id:
                            i['svc_ph'] = i['svc_ph'] + svc_ph
                            i['z_ph'] = i['z_ph'] + z_ph
                            i['cap_ph'] = i['cap_ph'] + cap_ph
                            i['ex_ph'] = i['ex_ph'] + ex_ph
            if move.move_type == 'in_refund':
                if move.partner_id not in list(map(itemgetter('partner'), data_refund)) not in data_refund:
                    r_svc_ph = 0
                    r_z_ph = 0
                    r_cap_ph = 0
                    r_ex_ph = 0
                    for invoice_lines in move.invoice_line_ids:
                        if invoice_lines.tax_ids.name in ['SVC-PH', 'Z-PH', 'CAP-PH', 'EX-PH'] and invoice_lines.tax_ids.type_tax_use == 'purchase':
                            if invoice_lines.tax_ids.name == 'SVC-PH':
                                r_svc_ph = invoice_lines.price_subtotal + r_svc_ph
                            if invoice_lines.tax_ids.name == 'Z-PH':
                                r_z_ph = invoice_lines.price_subtotal + r_z_ph
                            if invoice_lines.tax_ids.name == 'CAP-PH':
                                r_cap_ph = invoice_lines.price_subtotal + r_cap_ph
                            if invoice_lines.tax_ids.name == 'EX-PH':
                                r_ex_ph = invoice_lines.price_subtotal + r_ex_ph
                    data_refund.append({'partner': move.partner_id, 'r_svc_ph':
                                        r_svc_ph, 'r_z_ph': r_z_ph,
                                        'r_cap_ph': r_cap_ph, 'r_ex_ph': r_ex_ph})
                else:
                    r_svc_ph = 0
                    r_z_ph = 0
                    r_cap_ph = 0
                    r_ex_ph = 0
                    for invoice_lines in move.invoice_line_ids:
                        if invoice_lines.tax_ids.name in ['SVC-PH', 'Z-PH', 'CAP-PH', 'EX-PH'] and invoice_lines.tax_ids.type_tax_use == 'purchase':
                            if invoice_lines.tax_ids.name == 'SVC-PH':
                                r_svc_ph = invoice_lines.price_subtotal + r_svc_ph
                            if invoice_lines.tax_ids.name == 'Z-PH':
                                r_z_ph = invoice_lines.price_subtotal + r_z_ph
                            if invoice_lines.tax_ids.name == 'CAP-PH':
                                r_cap_ph = invoice_lines.price_subtotal + r_cap_ph
                            if invoice_lines.tax_ids.name == 'EX-PH':
                                r_ex_ph = invoice_lines.price_subtotal + r_ex_ph
                    for i in data_refund:
                        if i['partner'] == move.partner_id:
                            i['r_svc_ph'] = invoice_lines.price_subtotal + r_svc_ph
                            i['r_z_ph'] = invoice_lines.price_subtotal + r_z_ph
                            i['r_cap_ph'] = invoice_lines.price_subtotal + r_cap_ph
                            i['r_ex_ph'] = invoice_lines.price_subtotal + r_ex_ph
        for bill in data:
            for note in data_refund:
                if bill['partner'] == note['partner']:
                    bill['svc_ph'] = bill['svc_ph'] - note['r_svc_ph']
                    bill['z_ph'] = bill['z_ph'] - note['r_z_ph']
                    bill['cap_ph'] = bill['cap_ph'] - note['r_cap_ph']
                    bill['ex_ph'] = bill['ex_ph'] - note['r_ex_ph']
        return data

    def print_purchase_relief_excel_report(self):
        self.get_data()
        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        row_header_format = workbook.add_format(
            {'font_name': 'Calibri', 'font_size': 11, 'bold': 1,
             'align': 'center'})
        worksheet = workbook.add_worksheet('Purchase Relief reports')
        # worksheet.merge_range(
        #     0, 0, 0, 16, 'Purchase Order Relief Report', title_format)
        header_str = ['Vendor_TIN', 'companyName', 'lastName', 'firstName',
                      'middleName', 'address1', 'address2', 'exempt',
                      'zeroRated', 'services', 'capitalGoods', 'taxableNetofVat',
                      'vatRate', 'inputVat', 'totalPurchases']
        row_format = workbook.add_format(
            {'font_size': 10})
        row_format.set_text_wrap()
        align_center_bold = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': 1})
        align_center = workbook.add_format(
            {'font_size': 10, 'align': 'center'})
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 30)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        row = 0
        col = 0
        ex_total = 0
        z_total = 0
        svc_total = 0
        cap_total = 0
        net_vat_total = 0
        inpu_vat_total = 0
        total_purchase_total = 0
        for index, header in enumerate(header_str, start=0):
            worksheet.write(row, index, header, row_header_format)
        data_list = self.get_data()

        for data in data_list:
            row += 1
            partner = data.get('partner')
            worksheet.set_row(row, 35)
            worksheet.write(row, col, partner.vat,
                            align_center)
            worksheet.write(row, col + 1, partner.name or " ",
                            align_center)
            worksheet.write(row, col + 2, partner.awb_last_name or " ",
                            align_center)
            worksheet.write(row, col + 3, partner.awb_first_name or " ",
                            align_center)
            worksheet.write(row, col + 4, partner.awb_middle_name or " ",
                            align_center)
            if partner.street and partner.street2:
                worksheet.write(row, col + 5, partner.street + ', ' + partner.street2,
                                align_center)
            if partner.street and not partner.street2:
                worksheet.write(row, col + 5, partner.street,
                                align_center)
            if partner.street2 and not partner.street:
                worksheet.write(row, col + 5, partner.street2,
                                align_center)
            if partner.city and partner.state_id.name and partner.country_id.name:
                worksheet.write(row, col + 6, partner.city + ', ' + partner.state_id.name + ', ' + partner.country_id.name,
                                align_center)
            if partner.city and not partner.state_id.name and not partner.country_id.name:
                worksheet.write(row, col + 6, partner.city,
                                align_center)
            if partner.city and partner.state_id.name and not partner.country_id.name:
                worksheet.write(row, col + 6, partner.city + ', ' + partner.state_id.name,
                                align_center)
            if not partner.city and partner.state_id.name and not partner.country_id.name:
                worksheet.write(row, col + 6, partner.state_id.name,
                                align_center)
            if not partner.city and partner.state_id.name and partner.country_id.name:
                worksheet.write(row, col + 6, partner.state_id.name + ', ' + partner.country_id.name,
                                align_center)
            if not partner.city and not partner.state_id.name and partner.country_id.name:
                worksheet.write(row, col + 6, partner.country_id.name,
                                align_center)
            worksheet.write(row, col + 7, "{:,.2f}".format(data.get('ex_ph')),
                            align_center)
            worksheet.write(row, col + 8, "{:,.2f}".format(data.get('z_ph')),
                            align_center)
            worksheet.write(row, col + 9, "{:,.2f}".format(data.get('svc_ph')),
                            align_center)
            worksheet.write(row, col + 10, "{:,.2f}".format(data.get('cap_ph')),
                            align_center)
            net_vat = data.get('svc_ph') + data.get('cap_ph')
            input_vat = (net_vat * 12) / 100
            total_purchase = data.get(
                'ex_ph') + data.get('z_ph') + data.get('svc_ph') + data.get('cap_ph') + net_vat
            worksheet.write(row, col + 11, "{:,.2f}".format(net_vat),
                            align_center)
            worksheet.write(row, col + 12, 12,
                            align_center)
            worksheet.write(row, col + 13, "{:,.2f}".format(input_vat),
                            align_center)
            worksheet.write(row, col + 14, "{:,.2f}".format(total_purchase),
                            align_center)
            ex_total = ex_total + data.get('ex_ph')
            z_total = z_total + data.get('z_ph')
            svc_total = svc_total + data.get('svc_ph')
            cap_total = cap_total + data.get('cap_ph')
            net_vat_total = net_vat_total + net_vat
            inpu_vat_total = inpu_vat_total + input_vat
            total_purchase_total = total_purchase_total + total_purchase
        worksheet.write(row + 1, col + 7, "{:,.2f}".format(ex_total),
                        align_center_bold)
        worksheet.write(row + 1, col + 8, "{:,.2f}".format(z_total),
                        align_center_bold)
        worksheet.write(row + 1, col + 9, "{:,.2f}".format(svc_total),
                        align_center_bold)
        worksheet.write(row + 1, col + 10, "{:,.2f}".format(cap_total),
                        align_center_bold)
        worksheet.write(row + 1, col + 11, "{:,.2f}".format(net_vat_total),
                        align_center_bold)
        worksheet.write(row + 1, col + 13, "{:,.2f}".format(inpu_vat_total),
                        align_center_bold)
        worksheet.write(row + 1, col + 14, "{:,.2f}".format(total_purchase_total),
                        align_center_bold)
        # data
        workbook.close()
        fp.seek(0)
        result = base64.b64encode(fp.read())
        attachment_obj = self.env['ir.attachment']
        filename = 'Purchase Relief Report'
        attachment_id = attachment_obj.create(
            {'name': filename,
             'display_name': filename,
             'datas': result})
        download_url = '/web/content/' + \
                       str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
            'nodestroy': False,
        }
