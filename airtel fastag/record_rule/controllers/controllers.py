# -*- coding: utf-8 -*-
# from odoo import http


# class RecordRule(http.Controller):
#     @http.route('/record_rule/record_rule/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/record_rule/record_rule/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('record_rule.listing', {
#             'root': '/record_rule/record_rule',
#             'objects': http.request.env['record_rule.record_rule'].search([]),
#         })

#     @http.route('/record_rule/record_rule/objects/<model("record_rule.record_rule"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('record_rule.object', {
#             'object': obj
#         })
