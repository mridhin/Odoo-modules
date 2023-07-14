from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    service_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Service Status', compute="compute_sale_order")

    def compute_sale_order(self):
        for record in self:
            if record.order_line.task_id:
                order_line_length = len(record.order_line)
                new_count = 0
                comp_count = 0
                for rec in record.order_line:
                    if rec.task_id.stage_id.name == "Completed":
                        comp_count += 1
                    elif rec.task_id.stage_id.name == "New":
                        record.service_status = 'in_progress'
                        new_count += 1
                    else:
                        record.service_status = 'in_progress'
                        return False
                if new_count == order_line_length:
                    record.service_status = 'not_started'
                if comp_count == order_line_length:
                    record.service_status = 'completed'
            else:
                record.service_status = 'not_started'

    def write(self, vals):
        keys_to_check = ['payment_term_id', 'x_studio_ready_for_review_approval', 'x_studio_approved_by_category_head_1','x_studio_approved_by_category_head_2',
                         'x_studio_ready_for_review_approval', 'x_studio_available_service_schedule_domain']
        exceptional_key_to_check = ['x_studio_source_of_booking', 'x_studio_awb_service_type_id', 'x_studio_area_id',
                                    'x_studio_time_slot']
        if not any(key in vals for key in keys_to_check):
            if self.env.user.has_group('awb_sale_service.group_sale_booker'):
                raise UserError(_('Sorry, the created record is no longer editable'))
        elif any(key in vals for key in exceptional_key_to_check):
            if self.env.user.has_group('awb_sale_service.group_sale_booker'):
                raise UserError(_('Sorry, the created record is no longer editable'))
        return super(SaleOrder, self).write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    assigned_asc = fields.Many2one('res.users', string="Assigned ASC", compute="compute_assigned_asc")
    # assigned_asc_partner = fields.Many2one('res.partner', string="Assigned ASC(Partner)", compute="compute_assigned_asc")
    assign_other_asc = fields.Boolean(string='Assign other ASC?',compute="compute_assigned_asc")

    def compute_assigned_asc(self):
        for record in self:
            order_id = self.env['sale.order'].search([('id', '=', record.order_id.id)])
            for rec in order_id:
                record.assigned_asc = rec.x_studio_assigned_asc.id
                # record.assigned_asc_partner = rec.x_studio_partner_asc_id.id
                record.assign_other_asc = rec.x_studio_assign_other_asc

