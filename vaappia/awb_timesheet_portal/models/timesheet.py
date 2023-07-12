from odoo import models, fields, api, _
from odoo.osv import expression


class hr_timesheet(models.Model):
    _inherit = 'account.analytic.line'

    validated_status = fields.Selection(
        selection_add=[('submit', 'Submitted'),
                       ('approval_waiting', 'For Client Approval'),
                       ('validated', 'Approved'), ('rejected', 'Rejected'),
                       ],
        ondelete={'rejected': 'cascade',
                  'approval_waiting': 'cascade',
                  'submit': 'cascade'}, required=True,
        default="draft", store=True)
    rejected = fields.Boolean("Rejected", store=True, copy=False)
    submitted = fields.Boolean("Submitted", store=True, copy=False)
    client_approval = fields.Boolean('Client Approval', store=True, copy=False)
    area = fields.Selection(
        [('Outsystem', 'Outsystem'), ('Appia', 'Appia'), ('UI/UX', 'UI/UX'),
         ('Not_Applicable', 'Not Applicable'), ])
    project_type = fields.Char()
    #Added text field
    approver_notes = fields.Char('Approver Notes')
    
    @api.depends('validated', 'rejected', 'submitted', 'client_approval')
    def _compute_validated_status(self):
        for line in self:
            if line.validated:
                line.validated_status = 'validated'
            elif line.rejected:
                line.validated_status = 'rejected'
            elif line.submitted:
                line.validated_status = 'submit'
            elif line.client_approval:
                line.validated_status = 'approval_waiting'
            else:
                line.validated_status = 'draft'

        # res = super(hr_timesheet, self)._compute_validated_status()
        # return res

    def _timesheet_get_portal_domain(self):

        domain = super(hr_timesheet, self)._timesheet_get_portal_domain()
        # See all employees working for me on my projects
        return expression.AND([domain, [
                                        ('project_id.user_id', '=',
                                         self.env.user.id)]])
#         employee = self.env['hr.employee'].sudo().search(
#             [('user_id', '=', self.env.user.id)])
#         if employee:
#             print('emp')
#             return expression.AND([domain, [('employee_id', '=', employee.id)]])
# 
#         else:
#             # print('part')
#             # partner_domain = expression.AND([domain, [('project_id.partner_id', '=',self.env.user.partner_id.id)]])
#             # state_domain = expression.AND([domain, [
#             #     ('validated_status', '!=', 'draft')]])
# 
#             return expression.AND([domain, ['|', '&',
#                                             ('project_id.user_id', '=',
#                                              self.env.user.id), (
#                                             'project_id.partner_id', '=',
#                                             self.env.user.partner_id.id),
#                                             ('validated_status', '!=',
#                                              ["draft"])]])
       