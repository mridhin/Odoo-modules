# -*- coding: utf-8 -*-
# from odoo import http


# class ImpportUser(http.Controller):
#     @http.route('/impport_user/impport_user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/impport_user/impport_user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('impport_user.listing', {
#             'root': '/impport_user/impport_user',
#             'objects': http.request.env['impport_user.impport_user'].search([]),
#         })

#     @http.route('/impport_user/impport_user/objects/<model("impport_user.impport_user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('impport_user.object', {
#             'object': obj
#         })
