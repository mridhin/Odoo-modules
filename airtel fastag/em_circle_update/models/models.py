#-*- coding: utf-8 -*-

from odoo import models, fields, api


class EmUsers(models.Model):
    _inherit = "res.users"

    em_circle_custom = fields.Char(string='EM Circle', compute='_get_circle', store=True)
    rs_partner_name = fields.Char(string='Partner Name')

    @api.model
    @api.depends('rs_circle_ids')
    def _get_circle(self):
        for rec in self:
            if rec.rs_circle_ids:
                circle_custom = ','.join([p.name for p in rec.rs_circle_ids])
                rec.em_circle_custom = circle_custom
            else:
                rec.em_circle_custom = ''

    @api.onchange('rs_promoter', 'rs_employee')
    def emp_change(self):
        if self.rs_promoter is True:
            self.rs_designation = 'fastag_promoter'
        elif self.rs_employee is True:
            self.rs_designation = None
        group = self.env.ref('record_rule.group_enterprise_manager')
        print('group',group)

    # @api.onchange('rs_employee', 'rs_promoter')
    # def _onchange_groupl(self):
    #     group = self.env.ref('stock.group_stock_user')
    #     #user = self.search([('id','=',self.id)])
    #     user_id = self.browse(
    #         self._context.get('active_ids'))
    #     print('user',user_id.id)
    #     if self.rs_promoter == True:
    #         print('grouppp',group)
    #         group.update({
    #             'users': [(3,user_id.id)]
    #         })

    # @api.model
    # def create(self,values):
    #     res = super(EmUsers, self).create(values)
    #     group = self.env.ref('stock.group_stock_manager')
    #     print('grouppp',group)
    #     # if self.rs_employee == True:
    #     group.write({
    #         'users': [(3,self.id)]
    #         })
    #     return res