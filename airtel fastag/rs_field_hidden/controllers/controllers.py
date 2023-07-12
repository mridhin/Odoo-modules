# -*- coding: utf-8 -*-
# from odoo import http


# class FieldUpt(http.Controller):
#     @http.route('/field_upt/field_upt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/field_upt/field_upt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('field_upt.listing', {
#             'root': '/field_upt/field_upt',
#             'objects': http.request.env['field_upt.field_upt'].search([]),
#         })

#     @http.route('/field_upt/field_upt/objects/<model("field_upt.field_upt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('field_upt.object', {
#             'object': obj
#         })
