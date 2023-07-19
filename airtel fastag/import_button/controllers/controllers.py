# -*- coding: utf-8 -*-
# from odoo import http


# class ImportButton(http.Controller):
#     @http.route('/import_button/import_button/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_button/import_button/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_button.listing', {
#             'root': '/import_button/import_button',
#             'objects': http.request.env['import_button.import_button'].search([]),
#         })

#     @http.route('/import_button/import_button/objects/<model("import_button.import_button"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_button.object', {
#             'object': obj
#         })
