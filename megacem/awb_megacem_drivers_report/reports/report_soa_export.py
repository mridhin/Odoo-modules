# -*- coding: utf-8 -*-

from odoo import models, _
import io
import base64
from odoo.exceptions import UserError
from datetime import date
from odoo.tools.safe_eval import dateutil


class SOAXls(models.AbstractModel):
    _name = 'report.awb_megacem_drivers_report.report_dr_soa'
    _inherit = 'report.report_xlsx.abstract'

    def add_company_header(self, row, sheet, company, bold, merge_format, obj, date_style, customer_formate, br_format,
                           bt_format, bl_format):
        customer_name = ""
        address = ""
        zip = ""
        if len(obj.customer) > 1:
            raise UserError(_('Multiple customers selected.'))
        else:
            customer_name = obj.customer.name
        if obj.customer.street:
            address = f"{obj.customer.street} {obj.customer.street}"
        today = date.today()
        if obj.customer.vat:
            zip = obj.customer.vat
        if company.logo:
            product_image = io.BytesIO(base64.b64decode(company.logo))
            sheet.insert_image(row, 1, "image.png", {'image_data': product_image,
                                                     'x_scale': .40, 'y_scale': .40})
            sheet.write(row + 5, 1, "Bill To:", bl_format)
            sheet.write(row + 5, 2, "", bt_format)
            sheet.write(row + 5, 3, "", bt_format)
            sheet.write(row + 5, 4, "", br_format)

            sheet.write(row + 6, 1, "Customer:")
            sheet.write(row + 7, 1, customer_name, customer_formate)
            sheet.write(row + 8, 1, "Address:")
            sheet.write(row + 9, 1, address, customer_formate)
            sheet.write(row + 10, 1, "TIN No:")
            sheet.write(row + 11, 1, zip, customer_formate)
            sheet.write(4, 6, "Date:")
            sheet.write(4, 7, today, date_style)
            sheet.write(5, 6, "Statement No:")
            sheet.write(6, 6, "Invoice No:")
            sheet.write(7, 6, "FSPO No:")
            sheet.merge_range(2, 0, 2, 14, 'Billing Statement', merge_format)
            # sheet.merge_range(14, 1, 14, 14, 'This is to bill freight charges for the following deliveries:')

    def generate_xlsx_report(self, workbook, data, dr):
        row = 2
        count = 0
        if len(dr.customer) > 1:
            raise UserError(_('Multiple customers selected.'))
        sheet = workbook.add_worksheet(dr.customer.name)
        # sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        bold = workbook.add_format({'bold': True})
        br_format = workbook.add_format({'right': 5, 'top': 5, 'bottom': 5})
        bt_format = workbook.add_format({'top': 5, 'bottom': 5})
        bl_format = workbook.add_format({'left': 5, 'top': 5, 'bottom': 5})
        border = workbook.add_format({'border': 2})
        merge_format = workbook.add_format({'align': 'center', 'bold': True})
        cell_format = workbook.add_format({'align': 'center'})
        top_format = workbook.add_format({'align': 'center', 'top': 5, 'bottom': 5})
        left_format = workbook.add_format({'align': 'center', 'left': 5, 'top': 5, 'bottom': 5})
        right_format = workbook.add_format({'align': 'center', 'right': 5, 'top': 5, 'bottom': 5})
        date_style = workbook.add_format({'text_wrap': True, 'num_format': 'dd-mm-yyyy', 'align': 'center'})
        customer_formate = workbook.add_format({'align': 'right'})
        company = self.env.company

        self.add_company_header(row, sheet, company, bold, merge_format, dr, date_style, customer_formate,
                                br_format
                                , bt_format, bl_format)
        row += 13
        sheet.merge_range(row + 1, 1, row + 1, 14, 'This is to bill freight charges for the following deliveries:')
        row += 3
        sheet.write(row, 1, 'Date', left_format)
        sheet.write(row, 2, 'Shipment No.', top_format)
        sheet.write(row, 3, 'DR No.', top_format)
        sheet.write(row, 4, 'Plate No.', top_format)
        sheet.write(row, 5, 'Delivery Site 1', top_format)
        sheet.write(row, 6, 'Delivery Site 2', top_format)
        sheet.write(row, 7, 'Delivery Site 3', top_format)
        sheet.write(row, 8, 'Qty', top_format)
        sheet.write(row, 9, 'Unit Price', top_format)
        sheet.write(row, 10, 'Amount', right_format)
        gross_amount = 0
        for obj in dr:
            row += 1
            print(obj.created_on)
            count += 1
            x = dateutil.parser.parse(str(obj.created_on)).date()
            sheet.write(row, 0, count, customer_formate)
            sheet.write(row, 1, x, date_style)
            if obj.shipment_no:
                sheet.write(row, 2, obj.shipment_no, cell_format)
            sheet.write(row, 3, obj.name, cell_format)
            sheet.write(row, 4, obj.th_number.name, cell_format)
            if obj.delivery_site.name:
                sheet.write(row, 5, obj.delivery_site.name, cell_format)
            if obj.delivery_site_2.name:
                sheet.write(row, 6, obj.delivery_site_2.name, cell_format)
            if obj.delivery_site_3.name:
                sheet.write(row, 7, obj.delivery_site_3.name, cell_format)
            if obj.quantity_delivered or obj.quantity_delivered_2:
                sheet.write(row, 8, float(obj.quantity_delivered) + float(obj.quantity_delivered_2), cell_format)
            if obj.hauling_rate:
                sheet.write(row, 9, obj.hauling_rate, cell_format)
            sheet.write(row, 10, (float(obj.quantity_delivered) + float(obj.quantity_delivered_2)) * obj.hauling_rate)
            gross_amount += (float(obj.quantity_delivered) + float(obj.quantity_delivered_2)) * obj.hauling_rate
        print(row)
        formula = f"=sum(k20:k{row+1})"
        row += 1
        l_format = workbook.add_format({'left': 5, 'top': 5})
        lo_format = workbook.add_format({'left': 5})
        lob_format = workbook.add_format({'left': 5, 'bottom': 5})
        t_format = workbook.add_format({'top': 5})
        r_format = workbook.add_format({'right': 5, 'top': 5})
        ro_format = workbook.add_format({'right': 5})
        rob_format = workbook.add_format({'right': 5, 'bottom': 5})
        b_format = workbook.add_format({'bottom': 5})
        x_format = workbook.add_format({'bottom': 5, 'bold': True})
        sheet.write(row + 1, 1, "", l_format)
        sheet.write(row + 2, 1, "", lo_format)
        sheet.write(row + 3, 1, "", lo_format)
        sheet.write(row + 4, 1, "", lo_format)
        sheet.write(row + 5, 1, "", lob_format)
        sheet.write(row + 1, 2, "", t_format)
        sheet.write(row + 1, 3, "", t_format)
        sheet.write(row + 1, 4, "", t_format)
        sheet.write(row + 1, 5, "", t_format)
        sheet.write(row + 1, 6, "", t_format)
        sheet.write(row + 1, 7, "", t_format)
        sheet.write(row + 1, 9, "", t_format)
        sheet.write(row + 1, 10, "", r_format)
        sheet.write(row + 2, 10, "", ro_format)
        sheet.write(row + 3, 10, "", ro_format)
        sheet.write(row + 4, 10, "", ro_format)
        sheet.write(row + 5, 10, "", rob_format)
        sheet.write(row + 5, 2, "", b_format)
        sheet.write(row + 5, 3, "", b_format)
        sheet.write(row + 5, 4, "", b_format)
        sheet.write(row + 5, 5, "", b_format)
        sheet.write(row + 5, 6, "", b_format)
        sheet.write(row + 5, 7, "", b_format)
        sheet.write(row + 5, 9, "", b_format)
        sheet.write(row + 1, 8, 'Gross Amount', t_format)
        # sheet.write(row + 1, 10, formula, r_format)
        sheet.write_formula(row + 1, 10, formula, r_format, '')
        vat_formula = f"=(k{row+2}*12)/100"
        sheet.write(row + 2, 8, 'VAT')
        sheet.write_formula(row + 2, 10, vat_formula, ro_format, '')
        total_formula = f"=k{row + 2} + k{row + 3}"
        sheet.write(row + 3, 8, 'TOTAL')
        sheet.write_formula(row + 3, 10, total_formula, ro_format, '')
        sheet.write(row + 4, 8, 'EWT')
        sheet.write(row + 5, 8, 'Net Amount', x_format)
        sheet.write(row + 7, 1, 'Pesos:', bold)
        sheet.write(row + 9, 1, 'Note:', bold)

        sheet.write(row + 11, 1, 'Prepared by:')
        sheet.write(row + 11, 3, 'Checked by:')
        sheet.write(row + 11, 5, 'Noted by:')
        sheet.write(row + 11, 7, 'Received by:')

        sheet.write(row + 13, 7, 'Print Name/Sign & Date')
        sheet.write(row + 14, 1, 'ACCTG. SUPERVISOR')
        sheet.write(row + 14, 3, 'ACCTG. MANAGER')
        sheet.write(row + 14, 5, 'HRAD MANAGER')

        # create journal entry
        journal_obj = self.env['account.journal'].search([('name', '=', 'Billing Invoice')])

        recieveble_acc_id = self.env['account.account'].search([('code', '=', '2000022')])

        vat_acc_id = self.env['account.account'].search([('code', '=', '3000033')])

        income_acc_id = self.env['account.account'].search([('code', '=', '7000006')])

        line_ids = []
        journal_id = {'state': 'draft', 'move_type': 'entry', 'journal_id': journal_obj.id}
        vat_amount = (gross_amount * 12) / 100
        total_amount = gross_amount + vat_amount
        line_ids += [(0, 0, {'account_id': recieveble_acc_id.id, 'debit': total_amount
                             })
                     ]
        line_ids += [(0, 0, {'account_id': vat_acc_id.id, 'credit': vat_amount
                             })
                     ]
        line_ids += [(0, 0, {'account_id': income_acc_id.id, 'credit': gross_amount
                             })
                     ]
        journal_id.update({'line_ids': line_ids})
        move_id = self.env['account.move'].sudo().create(journal_id)

        for obj in dr:
            obj.update({'soa_journal_report': move_id.id})


