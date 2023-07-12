# -*- coding: utf-8 -*-
# from odoo import http


# class LogDetails(http.Controller):
#     @http.route('/log_details/log_details/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/log_details/log_details/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('log_details.listing', {
#             'root': '/log_details/log_details',
#             'objects': http.request.env['log_details.log_details'].search([]),
#         })

#     @http.route('/log_details/log_details/objects/<model("log_details.log_details"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('log_details.object', {
#             'object': obj
#         })
