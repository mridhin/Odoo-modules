# -*- coding: utf-8 -*-
# from odoo import http
# from odoo.http import request
# from datetime import datetime
# imports of odoo
import base64
import json
import werkzeug
import werkzeug.urls
import os
from odoo import http, tools
from odoo.http import request
from werkzeug.utils import secure_filename

from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools.translate import _

import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Transfer(http.Controller):

    # For render the website
    # @http.route('/ASC_accreditation_form', type='http', auth="public", website=True)
    @http.route(['/ASC_accreditation_form'], method='post', type='http',
                auth='public', website=True)
    def ASC_accreditation_form(self, **post):
        # return http.request.render('awb_asc_accreditation.ecom')
        response = http.Response(template='awb_asc_accreditation.ecom')
        submit_rec = []
        cities = []
        vals_nat = {}
        submit_rec = request.env['res.partner.industry'].sudo().search([('active', '=', True)])
        service_off = request.env['service.offered'].sudo().search([('ser_type', '=', 'services')])
        products_off = request.env['service.offered'].sudo().search([('ser_type', '=', 'products')])
        city = request.env['res.state.city'].sudo().search([], order='name asc')
        philippines_id = request.env["res.country"].sudo().search([('name', '=', 'Philippines')])
        state = request.env["res.country.state"].sudo().search([('country_id', '=', philippines_id.id)], order='name asc')
        vals_nat['submit_rec'] = submit_rec
        vals_nat['city'] = cities
        vals_nat['state'] = state
        vals_nat['country_id'] = philippines_id
        vals_nat['service_off'] = service_off
        vals_nat['products_off'] = products_off
        return request.render('awb_asc_accreditation.ecom', vals_nat)

    @http.route('/get_city_asc', type='http', auth='public', website=True)
    def get_city(self, **kw):
        """
        it is used to get cities of selected state
        """
        state = request.env['res.country.state'].sudo()
        if kw.get('region'):
            region = int(kw.get('region'))
            provience_id = state.sudo().browse(region)
            if provience_id.exists():
                city_ids = provience_id.city_ids
                city_list = ["<option>-select-</option>"]
                for city in city_ids:
                    option = "<option value= " + str(city.id) + ">" + city.name + "</option>"
                    city_list.append(option)
                option_value = '%s' % ' '.join(map(str, city_list))
        else:
            option_value = '%s' % ' '.join(map(str, ["<option>-select-</option>"]))
        return option_value

    @http.route('/join_now', type='http', auth="public", website=True)
    def my_method(self, **post):
        # Get the data submitted by the user
        # Get mob_no_code value
        file_base64 = ''
        error = "false"
        error_mob = "false"
        company_name = post.get('company_name')
        country_id = post.get('country_id')
        state_id = post.get('state_id')
        city = post.get('city')
        if city == '-select-':
            city = None

        city_obj = None
        if city is not None:
            city_obj = request.env['res.state.city'].sudo().search([('id', '=', city)])

        city_name = city_obj.name if city_obj is not None else None
        mob_no_code = post.get('mob_no_code')
        mob_no = post.get('mob_no')
        if mob_no:
            mob_val = len(mob_no)
            if mob_val != 10:
                error_mob = "true"
        email = post.get('email')
        name_of_bs = post.get('name_of_bs')
        if name_of_bs == '-select-':
            name_of_bs = None
        products_catered = request.httprequest.form.getlist('products')
        services_offered = request.httprequest.form.getlist('ser_off')
        prods = request.env['service.offered'].sudo().browse([int(prod_catered) for prod_catered in products_catered])
        servs = request.env['service.offered'].sudo().browse([int(serv_offered) for serv_offered in services_offered])

        def read_attachment(attachment):
            if post.get(attachment):
                name = request.httprequest.files.getlist(attachment)
                attachment_data = name[0].read()
                return base64.b64encode(attachment_data).replace(b'\n', b'')

        file = post.get('file_up', False)
        if file:
            file = post.get('file_up')
            attachment = file.read()
            file_size = len(attachment)
            file_base64 = base64.encodestring(attachment)
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1]
            len_file = len(file_ext)
            file = filename
            if file_ext not in ['.jpg', '.jpeg', '.png', '.pdf'] or file_size > 10000000:
                error = "true"
        # Create a dict to store and update the values in the res partner table

        record_dict = ({
            'company_type': 'company',
            'supplier_rank': 1,
            'name': company_name,
            'country_id': country_id,
            'state_id': int(post.get('state_id')),
            'city': city_name,
            'mobile': mob_no,
            'email': email,
            'x_studio_customer_classification': 'Regular',
            'nature_of_business_industry': name_of_bs,
            'products_catered_ids': prods,
            'services_offered_ids': servs,
            'letter_of_intent': read_attachment("letter_of_intent") if post.get("letter_of_intent") else False,
            'company_profile': read_attachment("company_profile") if post.get("company_profile") else False,
            'dti_bnr': read_attachment("dti_business_name_registration") if post.get(
                "dti_business_name_registration") else False,
            'dti_coa': read_attachment("dti_certificate_of_accreditation") if post.get(
                "dti_certificate_of_accreditation") else False,
            'business_mp': read_attachment("business_mayors_permit") if post.get("business_mayors_permit") else False,
            'bir_rc': read_attachment("bir_registration_certificate") if post.get(
                "bir_registration_certificate") else False,
            'orb_si': read_attachment("official_receipt_and_billing_service_invoice") if post.get(
                "official_receipt_and_billing_service_invoice") else False,
            'bac': read_attachment("brand_accreditation_certificate") if post.get(
                "brand_accreditation_certificate") else False,
            'sec_ai': read_attachment("sec_article_of_incorporation") if post.get(
                "sec_article_of_incorporation") else False,
            'cglip': read_attachment("comprehensive_gen_liability_insurance_policy") if post.get(
                "comprehensive_gen_liability_insurance_policy") else False,
            'pcab': read_attachment("pcab_contractors_license") if post.get("pcab_contractors_license") else False,
            'cosh_bosch': read_attachment("cosh_bosch_training_certificate") if post.get(
                "cosh_bosch_training_certificate") else False,
            'cpr': read_attachment("certificate_of_philgeps_registration") if post.get(
                "certificate_of_philgeps_registration") else False,
        })

        if mob_no:
            vals = {
                'record_dict': record_dict
            }
            vals['error_mob'] = error_mob
            val_mob = vals.get('error_mob')

            if val_mob == "true":
                return request.render('awb_asc_accreditation.ecom', {'val_mob': val_mob})
        if file:
            # Return a response to the user
            vals['error'] = error

            val = vals.get('error')
            if val == "true":
                return request.render('awb_asc_accreditation.ecom', {'val': val})
        if post:
            if error_mob == "false" and error == "false":
                val_join = "true"
                request.env['res.partner'].sudo().create(record_dict)
                # return request.render('awb_asc_accreditation.ecom', {'val_join': val_join})
