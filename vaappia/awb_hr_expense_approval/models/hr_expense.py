# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import Warning, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection(selection_add=[('for_approval', 'For Approval')], ondelete={'for_approval': 'cascade'})
    approval_lines = fields.One2many('hr.expense.approval.line', 'expense_id',
                                     string='Approval Lines', tracking=True, copy=True)
    #can_approve = fields.Boolean(compute='_compute_can_approve', store=True, default=False)
    button_visible = fields.Boolean(string='Approve', compute='_compute_button_visible')
    index_seq = fields.Integer(string='Index Sequence', default=1)
    reject_reason = fields.Text(string="Reject Reason")

    def _get_data_approvers(self, rule_id, condition, sequence, approver_id, add_seq=0):
        data = {
            'rule_id': rule_id,
            'approval_condition': condition,
            'sequence': sequence + add_seq,
            'approver_id': approver_id,
            'state': 'pending'
        }
        _logger.debug(f'data {data}')
        return data

    def action_for_approval(self):
        self.state = 'for_approval'
        args = [('active', '=', True),
                ('min_amount', '<=', self.total_amount),
                ('max_amount', '>', self.total_amount),]
        approval_rule = self.sudo().env['hr.expense.approval'].search(args, limit=1)

        approvers = []
        approvers_name = []
        add_seq =  0
        if approval_rule.employee_manager:
            if self.user_id:
                data = self._get_data_approvers(approval_rule.id, 'or', 1, self.user_id.id)
                approvers.append((0, 0, data))
                approvers_name.append(self.user_id.name)
                add_seq = 1
            else: 
                raise UserError(_('You need to set First Approver Manager to proceed.'))

        if approval_rule.department_manager:
            if approval_rule.employee_manager:
                if self.department_id.manager_id.user_id:
                    if self.department_id.manager_id.user_id.employee_id.id != self.employee_id.id and self.department_id.manager_id.user_id.name not in approvers_name:
                        data = self._get_data_approvers(approval_rule.id, 'and', 2, self.department_id.manager_id.user_id.id)
                        approvers.append((0, 0, data))
                        approvers_name.append(self.department_id.manager_id.user_id.name)
                else: 
                    raise UserError(_('You need to set Department Manager to proceed.'))

            else:
                if self.department_id.manager_id.user_id:
                    if self.department_id.manager_id.user_id.employee_id.id != self.employee_id.id and self.department_id.manager_id.user_id.name not in approvers_name:
                        data = self._get_data_approvers(approval_rule.id, 'and', 1, self.department_id.manager_id.user_id.id)
                        approvers.append((0, 0, data))
                        approvers_name.append(self.department_id.manager_id.user_id.name)
                        add_seq = 1
                else: 
                    raise UserError(_('You need to set Department Manager to proceed.'))

        for record in approval_rule.approver_ids:
            for approver in record.approved_by:
                if approver.employee_id.id != self.employee_id.id and approver.employee_id.name not in approvers_name:
                    data = self._get_data_approvers(approval_rule.id, record.approval_condition, record.sequence, approver.id, add_seq=add_seq)
                    approvers.append((0, 0, data))
                    approvers_name.append(self.department_id.manager_id.user_id.name)

                
        _logger.debug(f'APPROVERS {approvers}')
        self.sudo().update({'approval_lines': [(5, 0, 0)]})
        self.sudo().update({'approval_lines': approvers})

    def approve_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

    #         if not self.env.user in current_managers and not self.user_has_groups('hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
    #             raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'approve', 'user_id': responsible_id})
        self.activity_update()

    def action_approve(self):
        is_approved = False
        is_validate = False
        approval_condition = 'and'
        approval_status = []
        approvers = []
        args = [('state', '=', 'pending'),
                ('expense_id', '=', self.id),
                ('sequence', '=', self.index_seq)]

        approval_line_data = self.env['hr.expense.approval.line'].search(args)

        for approval in approval_line_data:
            approver = approval.approver_id.id
            approvers.append(approver)
            if approver == self.env.user.id:
                approval_condition = approval.approval_condition
                approval.state = 'approved'
                approval.can_proceed = True
            approval_status.append(approval.state)

        if approval_condition == 'or':
            is_approved = True
            for rec in approval_line_data:
                rec.can_proceed = True

            is_validate = all([line.can_proceed == True for line in self.approval_lines])
            _logger.debug(f'IS APPROVED IN CONDITION: {is_approved}')
            
        elif approval_condition == 'and':
            is_approved = all([state == 'approved' for state in approval_status])
            is_validate = all([line.can_proceed == True for line in self.approval_lines])

        _logger.debug(f'IS APPROVED: {is_approved}')
        _logger.debug(f'IS APPROVED Status: {approval_status}')
        _logger.debug(f'IS APPROVED COnditon: {approval_condition}')
        _logger.debug(f'IS VALIDATED: {is_validate}')
        if is_approved:
            self.index_seq += 1

            if approval_line_data:
                is_approved = False
                approval_status.clear()

        if is_validate:
            # self.state = 'sent'
            # self.reviewed_by = self.env.user.partner_id.id
            self.approve_expense_sheets()

    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'reject.wizard',
            'target': 'new',
        }
        # for approval in self.approval_lines:
        #     approver = approval.approver_id.id
        #     if approver == self.env.user.id:
        #         approval.sudo().update({'state': 'rejected'})
        # self.sudo().update({'state': 'submit'})
    def _compute_button_visible(self):
        if self.state == 'for_approval':
            args = [('state', '=', 'pending'),
                    ('expense_id', '=', self.id),
                    ('sequence', '=', self.index_seq)]

            approval_line_data = self.env['hr.expense.approval.line'].search(args)
            print('line',approval_line_data)
            if approval_line_data:
                approver = []
                for approval in approval_line_data:
                    if approval.state == 'pending':
                        approver.append(approval.approver_id.id)
                if self.env.user.id in approver:
                    self.sudo().update({'button_visible': True})
                else:
                    self.sudo().update({'button_visible': False})
            else:
                self.sudo().update({'button_visible': False})
        else:
            self.sudo().update({'button_visible': False})
    # @api.depends('state')
    # def _compute_can_approve(self):
    #     if self.env.is_superuser():
    #         self.sudo().update({'can_approve': True})
    #     else:
    #         self.sudo().update({'can_approve': False})
    #         if self.state == 'for_approval':
    #             can_approve = False
    #             args = [('state', '=', 'pending'),
    #                     ('expense_id', '=', self.id),
    #                     ('sequence', '=', self.index_seq)]
    #
    #             approval_line_data = self.env['hr.expense.approval.line'].search(args)
    #
    #             for approval in approval_line_data:
    #                 approver = approval.approver_id.id
    #                 _logger.debug(f'_compute_can_approve: {approver} {approval.state}')
    #                 if approver == self.env.user.id and approval.state == 'pending':
    #                     can_approve = True
    #
    #             if can_approve:
    #                 self.sudo().update({'can_approve': True})


class ReasonWizard(models.TransientModel):
    _name = 'reject.wizard'

    reject_reason = fields.Char(string="Reject Reason")

    def action_reject(self):
        expense_id = self.env['hr.expense.sheet'].browse(
            self._context.get('active_id', False))
        print(expense_id)
        for approval in expense_id.approval_lines:
            approver = approval.approver_id.id
            if approver == self.env.user.id:
                approval.sudo().update({'state': 'rejected', 'remarks': self.reject_reason})
        expense_id.sudo().update({'state': 'submit'})