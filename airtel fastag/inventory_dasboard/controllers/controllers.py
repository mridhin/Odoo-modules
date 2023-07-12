# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryDasboard(http.Controller):
#     @http.route('/inventory_dasboard/inventory_dasboard/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_dasboard/inventory_dasboard/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_dasboard.listing', {
#             'root': '/inventory_dasboard/inventory_dasboard',
#             'objects': http.request.env['inventory_dasboard.inventory_dasboard'].search([]),
#         })

#     @http.route('/inventory_dasboard/inventory_dasboard/objects/<model("inventory_dasboard.inventory_dasboard"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_dasboard.object', {
#             'object': obj
#         })
