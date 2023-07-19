# -*- coding: utf-8 -*-
# from odoo import http


# class OrderingSystem(http.Controller):
#     @http.route('/ordering_system/ordering_system/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ordering_system/ordering_system/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ordering_system.listing', {
#             'root': '/ordering_system/ordering_system',
#             'objects': http.request.env['ordering_system.ordering_system'].search([]),
#         })

#     @http.route('/ordering_system/ordering_system/objects/<model("ordering_system.ordering_system"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ordering_system.object', {
#             'object': obj
#         })
