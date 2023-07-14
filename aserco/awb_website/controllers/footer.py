# from odoo import http
from odoo import http
from odoo.http import request


class WebsiteFooter(http.Controller):
    @http.route('/store_directory', type='http',
                auth='public', website=True)
    def get_store_directory(self):
        return request.render("awb_website.store_directory")

    @http.route(['/testimonial'], method='post', type='http',
                auth='public', website=True)
    def get_feedback(self):
        testimonial_id = request.env['website.customer.testimonials'].sudo().search(
            [('published', '=', True)], order='id desc', limit=1)
        testimonial_ids = request.env['website.customer.testimonials'].sudo().search(
            [('published', '=', True)], order='id desc')
        values = {'testimonial_id': testimonial_id,
                  'testimonial_ids': testimonial_ids}
        response = http.Response(
            template='awb_website.feedback', qcontext=values)
        return response.render()
