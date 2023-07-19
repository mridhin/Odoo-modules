# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError

from collections import defaultdict


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'
    
    purchase_id = fields.Many2one(
        'purchase.order', string="Purchase")
    
    purchase_requester_id = fields.Many2one(
        'res.users', string="RFQ Requester")
    
    approval_type = fields.Selection(related="category_id.approval_type")
    
    x_studio_cost_distribution_charge = fields.Char(string="Cost Distribution / Charge")
    x_studio_executive_office = fields.Boolean(string="Executive Office")
    prf_finance = fields.Boolean(string="Finance")
    prf_operation_it = fields.Boolean(string="Operation / IT")
    prf_human_resource = fields.Boolean(string="Human Resource")
    prf_marketing = fields.Boolean(string="Marketing")
    prf_sales = fields.Boolean(string="Sales")
    prf_CE = fields.Boolean(string="CE")
    prf_PS = fields.Boolean(string="PS")
    prf_legal = fields.Boolean(string="Legal")
    prf_capex = fields.Boolean(string="Capex")
    prf_others = fields.Boolean(string="Others")
    prf_other_extra = fields.Char(string="Please Specify")
    x_studio_date_due = fields.Date(string="Date Due")
    
    
    @api.onchange("purchase_id")
    def onchange_purchase_id(self):
        if self.purchase_id:
            self.partner_id = self.purchase_id.partner_id.id
            self.amount = self.purchase_id.amount_total
            
            if self.purchase_id.order_line:
                product_line_ids = self.env['approval.product.line'].search([('purchase_order_line_id','in',self.purchase_id.order_line.ids)])
                if product_line_ids:
                    self.purchase_requester_id = product_line_ids.mapped("approval_request_id")[0].request_owner_id.id
                else:
                    self.purchase_requester_id = False
            
    @api.depends('category_id', 'request_owner_id','purchase_requester_id')
    def _compute_approver_ids(self):
        res = super()._compute_approver_ids()
        for request in self:
            
            # if request.purchase_id:
            #     if request.purchase_id.order_line:
            #         product_line_ids = self.env['approval.product.line'].search([('purchase_order_line_id','in',request.purchase_id.order_line.ids)])
            #         if product_line_ids:
            #             request.purchase_requester_id = product_line_ids.mapped("approval_request_id")[0].request_owner_id.id
            #         else:
            #             request.purchase_requester_id = False
            
            if request.category_id.approval_type == 'purchase_payment':
                if request.purchase_requester_id:
                    approver = request.approver_ids.filtered(lambda rec:rec.user_id.id == request.purchase_requester_id.id)
                    approver_id_vals = []
                    if not approver:
                        approver_id_vals.append(Command.create({
                            'user_id': request.purchase_requester_id.id,
                            'status': 'new',
                        }))
                        request.update({'approver_ids': approver_id_vals})
                approver_ids = request.approver_ids.filtered(lambda rec:rec.user_id.employee_id.approve_type != 'om')
                remove_approver_ids = approver_ids.filtered(lambda rec:rec.user_id.id != request.purchase_requester_id.id)
                for remove_approver_id in remove_approver_ids:
                    request.update({'approver_ids': [(3, remove_approver_id.id)]})
    
    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            required_statuses = request.approver_ids.filtered('required').mapped('status')
            required_approved = required_statuses.count('approved') == len(required_statuses)
            minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(status_lst)
            if status_lst:
                if (self.category_id.sequence_code == 'APPR') or (self.category_id.approval_type == 'purchase') or (self.category_id.approval_type == 'purchase_payment'):
                    
                    if status_lst.count('cancel'):
                        status = 'cancel'
                    elif status_lst.count('refused'):
                        status = 'refused'
                    elif status_lst.count('pending'):
                        status = 'pending'
                    elif status_lst.count('approved') >= minimal_approver and required_approved:
                        status = 'approved'
                    else:
                        status = 'new'
                    
                else:  
                    if status_lst.count('cancel'):
                        status = 'cancel'
                    elif status_lst.count('refused'):
                        status = 'refused'
                    elif status_lst.count('new'):
                        status = 'new'
                    elif status_lst.count('approved') >= minimal_approver and required_approved:
                        status = 'approved'
                    else:
                        status = 'pending'
            else:
                status = 'new'
            request.request_status = status
    
    def action_approve(self, approver=None):
        res = super().action_approve(approver)
        
        if self.category_id.sequence_code == 'APPR' or self.category_id.approval_type == 'purchase':
            self.purchase_approval_process()
        elif self.category_id.approval_type == 'purchase_payment':
            self.purchase_payment_approval_process()
            
        return res
    
    def action_confirm(self):
        
        for request in self:
            if request.approval_type == 'purchase' and not request.product_line_ids:
                raise UserError(_("You cannot create an empty purchase request."))
        
        # make sure that the manager is present in the list if he is required
        self.ensure_one()
        if self.category_id.manager_approval == 'required':
            employee = self.env['hr.employee'].search([('user_id', '=', self.request_owner_id.id)], limit=1)
            if not employee.parent_id:
                raise UserError(_('This request needs to be approved by your manager. There is no manager linked to your employee profile.'))
            if not employee.parent_id.user_id:
                raise UserError(_('This request needs to be approved by your manager. There is no user linked to your manager.'))
            if not self.approver_ids.filtered(lambda a: a.user_id.id == employee.parent_id.user_id.id):
                raise UserError(_('This request needs to be approved by your manager. Your manager is not in the approvers list.'))
        if len(self.approver_ids) < self.approval_minimum:
            raise UserError(_("You have to add at least %s approvers to confirm your request.", self.approval_minimum))
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))
        
        if self.category_id.sequence_code == 'APPR' or self.category_id.approval_type == 'purchase':
            self.purchase_approval_process()
        elif self.category_id.approval_type == 'purchase_payment':
            self.purchase_payment_approval_process()
        else:
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
            approvers._create_activity()
            approvers.write({'status': 'pending'})
        self.write({'date_confirmed': fields.Datetime.now()})
        
    def purchase_approval_process(self):
        if (self.amount >= self.company_id.po_double_validation_amount) or (self.request_owner_id.employee_id.approve_type == 'dm'):
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new' and approver.user_id.employee_id.approve_type == 'dm')
            if approvers:
                approvers._create_activity()
                approvers.write({'status': 'pending'})
            else:
                approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new' and approver.user_id.employee_id.approve_type == 'ceo')
                if approvers:
                    approvers._create_activity()
                    approvers.write({'status': 'pending'})
                else:
                    approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new' and approver.user_id.employee_id.approve_type == 'om')
                    if approvers:
                        approvers._create_activity()
                        approvers.write({'status': 'pending'})
        else:
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new' and approver.user_id.employee_id.approve_type == 'dm')
            if approvers:
                approvers._create_activity()
                approvers.write({'status': 'pending'})
            else:
                approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new' and approver.user_id.employee_id.approve_type == 'om')
                if approvers:
                    approvers._create_activity()
                    approvers.write({'status': 'pending'})
                    
    def purchase_payment_approval_process(self):
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new' and approver.user_id.id == self.purchase_requester_id.id)
        
        if approvers:
            approvers._create_activity()
            approvers.write({'status': 'pending'})
        else:
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new' and approver.user_id.employee_id.approve_type == 'om')
            if approvers:
                approvers._create_activity()
                approvers.write({'status': 'pending'})

    
    
    
