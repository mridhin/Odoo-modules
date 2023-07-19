# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class vehical(http.Controller):
    @http.route('/picking', type="json", auth='public')
    def get_picking(self):
        picking_id = request.env['stock.picking'].search([])
        picking_list = []
        for rec in picking_id:
            val = {
                'name':rec.name
            }
            picking_list.append(val)
        data = {'status': 200,'response':picking_list, 'messages': 'sucess'}
        return data

    @http.route('/product/list', type="json", auth='public')
    def get_picking(self):
        product_id = request.env['product.product'].search([])
        product_list = []
        for rec in product_id:
            val = {
                'id':rec.id,
                'name': rec.name
            }
            product_list.append(val)
        data = {'status': 200, 'response': product_list, 'messages': 'sucess'}
        return data

    @http.route('/user/create', type="json", auth='user')
    def create_user(self,**rec):
        if request.jsonrequest:
            val = {
                'name': rec['name'],
                'login': rec['login']
            }
            new_user = http.request.env['res.users'].sudo.create(val)
            data = {'success': True, 'message': 'success', 'ID': new_user.id}
            return data


#     @http.route('/nbq_sla/nbq_sla/objects/<model("nbq_sla.nbq_sla"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nbq_sla.object', {
#             'object': obj
#         })
