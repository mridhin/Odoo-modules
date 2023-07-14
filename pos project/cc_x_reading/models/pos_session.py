import base64

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.osv.expression import AND


class PosSession(models.Model):
    _inherit = "pos.session"

    def generate_x_reading_report(self, cc_x_reading_id):
        cc_x_reading_id.is_x_reading = True
        cc_x_reading_id._get_cashier_ids()
        data = {
            'cashier_ids': cc_x_reading_id.cashier_ids,
            'taxpayer_min': self.taxpayer_min,
            'taxpayer_machine_serial_number': self.taxpayer_machine_serial_number,
            'awb_pos_provider_ptu': self.awb_pos_provider_ptu,
            'reference': cc_x_reading_id.reference,
            'date_start': cc_x_reading_id.start_date,
            'date_stop': cc_x_reading_id.end_date,
            'company_name': cc_x_reading_id.env.company.name,
            'total_sales': cc_x_reading_id.total_sales,
            # 'total_returns': cc_x_reading_id.total_returns,
            'total_voids': cc_x_reading_id.total_voids,
            'total_discounts': cc_x_reading_id.total_discounts,
            'subtotal': cc_x_reading_id.subtotal,
            'vatable_sales': cc_x_reading_id.vatable_sales,
            'vat_12': cc_x_reading_id.vat_12,
            'vat_exempt_sales': cc_x_reading_id.vat_exempt_sales,
            'zero_rated_sales': cc_x_reading_id.zero_rated_sales,
            'register_total': cc_x_reading_id.register_total,
            'beginning_reading': cc_x_reading_id.beginning_reading,
            'ending_reading': cc_x_reading_id.ending_reading,
            'regular_discount': cc_x_reading_id.regular_discount,
			'pricelist_amount': cc_x_reading_id.pricelist_amount,
			'sc_pwd_vat_in': cc_x_reading_id.sc_pwd_vat_in,
			'sc_vat_ex': cc_x_reading_id.sc_vat_ex,
			'pwd_vat_ex': cc_x_reading_id.pwd_vat_ex,
        }
        data.update(cc_x_reading_id.get_x_reading_payments(data['date_start'], data['date_stop']))

        return data

    def clossing_session_x_reading_report(self):
        """
            Reformatted end_date since the previous code is capturing the milliseconds
                and will result to conflicts during ORM search. By default, Odoo is not saving
                the milliseconds. Increase seconds as well to accomodate for 
                increase in calculation time.
        """
        cc_x_reading_id = self.env['cc_x_reading.x_reading'].with_context(pos_close_report=True, session=self.id).create({
            'start_date': self.start_at,
            'end_date': fields.datetime.now().replace(microsecond=0) + timedelta(seconds=15),
            'crm_team_id': self.crm_team_id.id,
            'session_ids': [(6, 0, [self.id])],
            'session_id' : self.id,
            'config_id' : self.config_id.id,
        })

        data = self.generate_x_reading_report(cc_x_reading_id)
        pdf = self.env.ref('cc_x_reading.action_x_reading_report').sudo()._render_qweb_pdf(cc_x_reading_id.id, data)[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        result = base64.b64encode(pdf)
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.sudo().create(
            {'name': "X-Reading", 'store_fname': 'name.pdf', 'datas': result})
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        # print(result)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {"url": str(base_url) + str(download_url)}
