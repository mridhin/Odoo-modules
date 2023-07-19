# -*- coding: utf-8 -*-
# from odoo import http


# class UnlinkedTag(http.Controller):
#     @http.route('/unlinked_tag/unlinked_tag/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/unlinked_tag/unlinked_tag/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('unlinked_tag.listing', {
#             'root': '/unlinked_tag/unlinked_tag',
#             'objects': http.request.env['unlinked_tag.unlinked_tag'].search([]),
#         })

#     @http.route('/unlinked_tag/unlinked_tag/objects/<model("unlinked_tag.unlinked_tag"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('unlinked_tag.object', {
#             'object': obj
#         })
