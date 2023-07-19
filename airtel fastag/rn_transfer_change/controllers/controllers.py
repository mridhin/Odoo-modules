# -*- coding: utf-8 -*-
# from odoo import http


# class RnTransferChange(http.Controller):
#     @http.route('/rn_transfer_change/rn_transfer_change/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rn_transfer_change/rn_transfer_change/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rn_transfer_change.listing', {
#             'root': '/rn_transfer_change/rn_transfer_change',
#             'objects': http.request.env['rn_transfer_change.rn_transfer_change'].search([]),
#         })

#     @http.route('/rn_transfer_change/rn_transfer_change/objects/<model("rn_transfer_change.rn_transfer_change"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rn_transfer_change.object', {
#             'object': obj
#         })
