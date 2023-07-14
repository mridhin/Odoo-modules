# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime


class zReadingInherit(models.Model):
    _inherit='cc_x_reading.x_reading'
    
    
    begin_or_no = fields.Char(compute='_compute_reading_values', search='_search_reading_values')
    end_or_no = fields.Char()
    acc_beginning = fields.Float()
    acc_end = fields.Float()
    acc_beginning_no = fields.Char()
    acc_end_no = fields.Char()
    
    def _compute_reading_values(self):
        """"compute field trigger"""
        for record in self:
            record._query_x_receipts()
        
    def _search_reading_values(self):
        """"search method trigger"""
        for i in self:
            order_ids = i.session_id.order_ids
            if order_ids:
                i.begin_or_no = order_ids[-1].pos_reference
                i.end_or_no = order_ids[0].pos_reference
                
    def _query_x_receipts(self):
        """this is used to calculate the order number, beg- accumulated amount and ref"""
        
        s_date = self.session_id.start_at
        vals = []
        new_vals = []
        # if self.session_id:
        self._cr.execute(""" 
                select min(ps.id) as session_min_id, max(ps.id) as session_max_id, min(pos.id) as po_min_id, max(pos.id) as po_max_id,
                (select min(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_min_id,
                (select max(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_max_id,
                (select sum(amount_total) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_amount
                from pos_session ps join pos_order pos on pos.session_id = ps.id 
                where cast(ps.start_at as date) = '%s' and pos.session_id = '%s'
        
        """ % (str(s_date.date()), str(self.session_id.id)))

        val_0 = self._cr.dictfetchall()
        vals.append(val_0[0])
        previous_Date = s_date.date() - datetime.timedelta(days=1)

        self._cr.execute(""" 
            select min(ps.id) as session_min_id, max(ps.id) as session_max_id, min(pos.id) as po_min_id, max(pos.id) as po_max_id,
            (select min(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_min_id,
            (select max(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_max_id,
            (select sum(amount_total) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_amount
            from pos_session ps join pos_order pos on pos.session_id = ps.id 
            where cast(ps.start_at as date) = '%s' and pos.session_id = '%s'
    
        """ % (str(s_date.date()), str(self.session_id.id)))
    
        val_1 = self._cr.dictfetchall()
        new_vals.append(val_1[0])

        max_ref = ''
        min_ref = ''
        
        if len(vals) > 0:
            order = self.env['pos.order']
            am = self.env['account.move']
            min_order = order.search([('id', '=', vals[0].get('po_min_id'))])
            max_order = order.search([('id', '=', vals[0].get('po_max_id'))]) 
            adj_min = order.search([('id', '=', vals[0].get('adj_min_id'))])
            adj_max = order.search([('id', '=', vals[0].get('adj_max_id'))])
            if adj_max:
                max_ref = am.search([('pos_order_id','=', adj_max.id)])
                print('max_ref',max_ref)
            if adj_min:
                min_ref = am.search([('pos_order_id','=', adj_min.id)])
                print('min_ref',min_ref)
                
            if not adj_max:
                """"changed the variable to the adj_min, because it fetch the values from previous date."""
                adj_min = order.search([('id', '=', new_vals[0].get('adj_max_id'))])
                if adj_min:
                    min_ref = am.search([('pos_order_id','=', adj_min.id)])
                    print(min_ref)
            print(min_order, max_order, adj_min, adj_max)
            
            if self.session_id:
                if adj_max:
                    if not (adj_max.id == adj_min.id):
                        ad_max = round(abs(adj_max.amount_total), 0) + round(abs(adj_min.amount_total), 0)
                    else:
                        ad_max = round(abs(adj_max.amount_total), 0)
                else:
                    ad_max = 0.00 + round(abs(adj_min.amount_total), 0)
            else:
                ad_max = round(abs(vals[0].get('adj_amount')), 0)
            
            #to update the order sequence number
            self.begin_or_no = min_order.pos_reference
            self.end_or_no = max_order.pos_reference
            #to update the accumulated amount
            self.acc_beginning = round(abs(adj_min.amount_total), 0)
            self.acc_end = ad_max
            #to update the ref
            self.acc_beginning_no = min_ref.name if min_ref else ''
            self.acc_end_no = max_ref.name if max_ref else ''