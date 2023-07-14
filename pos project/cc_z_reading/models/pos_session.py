import base64

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.osv.expression import AND


class PosSession(models.Model):
    _inherit = "pos.session"

    last_z_reading = fields.Boolean(default=False)

    def generate_report(self, cc_z_reading_id):
        self.last_z_reading = True
        cc_z_reading_id.is_z_reading = True
        cc_z_reading_id.session_id = self.id
        cc_z_reading_id._get_cashier_ids() 
        data = {
            'cashier_ids': cc_z_reading_id.cashier_ids,
            'reference': cc_z_reading_id.reference,
            'taxpayer_min': self.taxpayer_min,
            'taxpayer_machine_serial_number': self.taxpayer_machine_serial_number,
            'awb_pos_provider_ptu': self.awb_pos_provider_ptu,
            'date_start': cc_z_reading_id.start_date,
            'date_stop': cc_z_reading_id.end_date,
            'company_name': cc_z_reading_id.env.company.name,
            'total_sales': cc_z_reading_id.total_sales,
            # 'total_returns': cc_z_reading_id.total_returns,
            'total_voids': cc_z_reading_id.total_voids,
            'total_discounts': cc_z_reading_id.total_discounts,
            'subtotal': cc_z_reading_id.subtotal,
            'vatable_sales': cc_z_reading_id.vatable_sales,
            'vat_12': cc_z_reading_id.vat_12,
            'vat_exempt_sales': cc_z_reading_id.vat_exempt_sales,
            'zero_rated_sales': cc_z_reading_id.zero_rated_sales,
            'register_total': cc_z_reading_id.register_total,
            'beginning_reading': cc_z_reading_id.beginning_reading,
            'ending_reading': cc_z_reading_id.ending_reading,
            'regular_discount': cc_z_reading_id.regular_discount,
			'pricelist_amount': cc_z_reading_id.pricelist_amount,
			'sc_pwd_vat_in': cc_z_reading_id.sc_pwd_vat_in,
			'sc_vat_ex': cc_z_reading_id.sc_vat_ex,
			'pwd_vat_ex': cc_z_reading_id.pwd_vat_ex,
            'begin_or_no':cc_z_reading_id.begin_or_no,
            'end_or_no':cc_z_reading_id.end_or_no,
            'acc_beginning': cc_z_reading_id.acc_beginning,
            'acc_end': cc_z_reading_id.acc_end,
            'acc_beginning_no': cc_z_reading_id.acc_beginning_no,
            'acc_end_no': cc_z_reading_id.acc_end_no,
        }
        data.update(cc_z_reading_id.get_payments(data['date_start'], data['date_stop']))

        return data

    def clossing_session_report(self):
        """
            Capture last_z_reading
            Search for last_z_reading = True in records;
            Use the start_at of that record;
            Check if record exists
                expect empty record > handle error
                    if blank: use self as start_at
        """
        last_pos_session_with_z_reading = self.search([('last_z_reading', '=', True)], limit=1)
        scope_session_ids = self.search([('id', '>', last_pos_session_with_z_reading.id), ('config_id', '=', self.config_id.id)], order='id asc')

        if scope_session_ids:
            """
                Reformatted end_date since the previous code is capturing the milliseconds
                    and will result to conflicts during ORM search. By default, Odoo is not saving
                    the milliseconds. Increase seconds as well to accomodate for 
                    increase in calculation time.
            """
            cc_z_reading_id = self.env['cc_z_reading.z_reading'].with_context(pos_close_report=True).create({
                'start_date': scope_session_ids[0].start_at,
                'end_date': fields.datetime.now().replace(microsecond=0) + timedelta(seconds=15),
                'crm_team_id': self.crm_team_id.id,
                'config_id' : self.config_id.id,
                #'session_ids': [(6, 0, self.ids)],
                'session_ids': [(6, 0, scope_session_ids.ids)],
            })

        else:
            """
                Reformatted end_date since the previous code is capturing the milliseconds
                    and will result to conflicts during ORM search. By default, Odoo is not saving
                    the milliseconds. Increase seconds as well to accomodate for 
                    increase in calculation time.
            """
            cc_z_reading_id = self.env['cc_z_reading.z_reading'].with_context(pos_close_report=True).create({
                'start_date': self.start_at,
                'end_date': fields.datetime.now().replace(microsecond=0) + timedelta(seconds=15),
                'crm_team_id': self.crm_team_id.id,
                'config_id' : self.config_id.id,
                'session_ids': [(6, 0, self.ids)],
            })

        data = self.generate_report(cc_z_reading_id)
        pdf = self.env.ref('cc_z_reading.action_z_reading_report').sudo()._render_qweb_pdf(cc_z_reading_id.id, data)[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        result = base64.b64encode(pdf)
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.sudo().create(
            {'name': "Z-reading", 'store_fname': 'name.pdf', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        # print(result)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {"url": str(base_url) + str(download_url)}
