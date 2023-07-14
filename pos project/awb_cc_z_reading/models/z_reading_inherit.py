# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime




class zReadingInherit(models.Model):
    _inherit='cc_z_reading.z_reading'
    
    
    begin_or_no = fields.Char(compute='_compute_reading_values', search='_search_reading_values')
    end_or_no = fields.Char()
    acc_beginning = fields.Float()
    acc_end = fields.Float()
    acc_beginning_no = fields.Char()
    acc_end_no = fields.Char()
    
    def _compute_reading_values(self):
        """"compute field trigger"""
        for record in self:
            record._query_z_receipts()
        
    def _search_reading_values(self):
        """"search method trigger"""
        for i in self:
            order_ids = i.session_id.order_ids
            if order_ids:
                self.begin_or_no = order_ids[-1].pos_reference
                self.end_or_no = order_ids[0].pos_reference
                
    def _query_z_receipts(self):
        """this is used to calculate the order number, beg- accumulated amount and ref, updated changes"""
        
        
        s_date = self.session_id.start_at
        config_id = self.session_id.config_id
        vals = []
        new_vals = []
        if self.session_id:
            self._cr.execute(""" 
                    select min(ps.id) as session_min_id, max(ps.id) as session_max_id, min(pos.id) as po_min_id, max(pos.id) as po_max_id,
                    (select min(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_min_id,
                    (select max(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_max_id,
                    (select sum(amount_total) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_amount
                    from pos_session ps join pos_order pos on pos.session_id = ps.id 
                    where cast(ps.start_at as date) = '%s' and ps.config_id = %s
            
            """ % (str(s_date.date()), config_id.id))
            
            val_0 = self._cr.dictfetchall()
            vals.append(val_0[0])
            
            previous_Date = s_date.date() - datetime.timedelta(days=1)
            
        
       
            self._cr.execute(""" 
                select min(ps.id) as session_min_id, max(ps.id) as session_max_id, min(pos.id) as po_min_id, max(pos.id) as po_max_id,
                (select min(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_min_id,
                (select max(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_max_id,
                (select sum(amount_total) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_amount
                from pos_session ps join pos_order pos on pos.session_id = ps.id 
                where cast(ps.start_at as date) = '%s' and ps.config_id = %s
        
            """ % (str(previous_Date), config_id.id))
        
            val_1 = self._cr.dictfetchall()
            new_vals.append(val_1[0])
        
        else:
            start_date = self.start_date
            end_date = self.end_date
            crm_id = self.crm_team_id
            pos_config = self.env['pos.config'].sudo().search([('crm_team_id', '=', crm_id.id)])
            #print(str(pos_config.ids)[1:-1])
            
            self._cr.execute("""
                select min(ps.id) as session_min_id, max(ps.id) as session_max_id, min(pos.id) as po_min_id, max(pos.id) as po_max_id,
                (select min(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_min_id,
                (select max(id) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_max_id,
                (select sum(amount_total) from pos_order where id >= min(pos.id) and id <= max(pos.id) and amount_total < 0.0) as adj_amount
                from pos_session ps join pos_order pos on pos.session_id = ps.id 
                where cast(ps.start_at as date) >= '%s' and cast(ps.stop_at as date) <= '%s' and ps.config_id in (%s)
            """  % (str(start_date), str(end_date), str(pos_config.ids)[1:-1]))
            
            val_0 = self._cr.dictfetchall()
            vals.append(val_0[0])
            new_vals.append(val_0[0])
        
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
                #print('max_ref',max_ref)
            if adj_min:
                min_ref = am.search([('pos_order_id','=', adj_min.id)])
                #print('min_ref',min_ref)
                
            if not adj_max:
                """"changed the variable to the adj_min, because it fetch the values from previous date."""
                adj_min = order.search([('id', '=', new_vals[0].get('adj_max_id'))])
                if adj_min:
                    min_ref = am.search([('pos_order_id','=', adj_min.id)])
                    #adj_min = abs(adj_min.amount_total)
                    
                    #print(min_ref)
            #print(min_order, max_order, adj_min, adj_max)
            
            if self.session_id:
                if adj_max:
                    if not (adj_max.id == adj_min.id):
                        ad_max = abs(vals[0].get('adj_amount'))
                        adj_min = abs(adj_min.amount_total)
                    else:
                        if (adj_max.id == adj_min.id):
                            adj_min = 0.00
                            min_ref = ''
                        else:
                            adj_min = abs(adj_min.amount_total)
                        ad_max = abs(adj_max.amount_total)
                else:
                    ad_max = 0.00 + abs(adj_min.amount_total)
                    adj_min = 0.00
            else:
                ad_max = 0.00
                adj_min = 0.00
                if vals[0].get('adj_amount'):
                    ad_max = abs(vals[0].get('adj_amount'))
                if adj_min:
                    adj_min = abs(adj_min.amount_total)
            
            #to update the order sequence number
            self.begin_or_no = min_order.pos_reference
            self.end_or_no = max_order.pos_reference
            #to update the accumulated amount
            self.acc_beginning = adj_min 
            self.acc_end = ad_max
            #to update the ref
            
            #update the min ref value
            #cdate = datetime.now()
            s_date = self.session_id.start_at
            if self.session_id:
                config_id = self.session_id.config_id
                if s_date:
                    #ending
                    self._cr.execute("""
                        select max(po.id) as id from pos_order po inner join pos_session ps on po.session_id = ps.id
                            where po.amount_total < 0.0 
                            and cast(po.date_order as date) = '%s'
                            and ps.config_id = %s
                    """ %(str(s_date.date()), config_id.id))
                    e_value = self._cr.dictfetchall()
                    
                    #beginning
                    self._cr.execute("""
                        select max(po.id) as id from pos_order po inner join pos_session ps on po.session_id = ps.id
                            where po.amount_total < 0.0 
                            and cast(po.date_order as date) < '%s'
                            and ps.config_id = %s
                    """ %(str(s_date.date()), config_id.id))
                    b_value = self._cr.dictfetchall()
                    
                    amove = self.env['account.move']
                    posOrder  = self.env['pos.order']
                
                    b_refer = ''
                    e_refer = ''
                    if b_value[0].get('id'):
                        b_id = b_value[0]
                        min_id = posOrder.browse(b_id.get('id'))
                        b_cn = amove.search([('pos_order_id','=', min_id.id)])
                        b_refer = b_cn.name
                    else:
                        b_refer = '0'
                    
                    if e_value[0].get('id'):
                        e_id = e_value[0]
                        max_id = posOrder.browse(e_id.get('id'))
                        e_cn = amove.search([('pos_order_id','=', max_id.id)])
                        e_refer = e_cn.name
                    else:
                        e_refer = b_refer
                    
                    min_ref = b_refer
                    max_ref = e_refer

            self.acc_beginning_no = min_ref if min_ref else ''
            self.acc_end_no = max_ref if max_ref else ''
            
