# -*- coding: utf-8 -*-
# from odoo import http


# class EmCircleUpdate(http.Controller):
#     @http.route('/em_circle_update/em_circle_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/em_circle_update/em_circle_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('em_circle_update.listing', {
#             'root': '/em_circle_update/em_circle_update',
#             'objects': http.request.env['em_circle_update.em_circle_update'].search([]),
#         })

#     @http.route('/em_circle_update/em_circle_update/objects/<model("em_circle_update.em_circle_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('em_circle_update.object', {
#             'object': obj
#         })
