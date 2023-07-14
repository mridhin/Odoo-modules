# -*- coding: utf-8 -*-
# from odoo import http
from odoo import http
from odoo.http import request
import datetime
import requests
from bs4 import BeautifulSoup


class WebsiteHome(http.Controller):
    @http.route(['/'], method='post', type='http',
                auth='public', website=True)
    def get_service_blog(self):
        web_my_service_ids = request.env['calendar.appointment.type'].sudo().search(
            [('active', '=', True), ('is_published', '=', True)])
        testimonial_ids = request.env['website.customer.testimonials'].sudo().search(
            [('published', '=', True)], order='id desc', limit=3)
        values = {'testimonial_ids': testimonial_ids,
                  'web_my_service_ids': web_my_service_ids}
        response = http.Response(
            template='awb_website.acerco_homepage', qcontext=values)
        return response.render()

