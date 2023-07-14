# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import datetime, json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    assigned_asc_sale = fields.Many2one('res.partner', 'Assigned ASC')
    assigned_asc_sale_domain = fields.Char('Assigned ASC Domain')
    assigned_asc_count = fields.Integer('Assigned ASC Count')
    assigned_asc_count_partner = fields.Integer('Assigned ASC Count Partner')

    @api.onchange('x_studio_area_id', 'x_studio_assign_other_asc', 'x_studio_awb_service_type_id',
                  'x_studio_service_needed', 'x_studio_service_needed_1', 'x_studio_service_needed_2',
                  'x_studio_time_slot', 'x_studio_preferred_service_schedule')
    def filter_assigned_asc_field(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        date_list = [(tomorrow + datetime.timedelta(days=x)).date() for x in range(30)]

        allocated_technician_line = self.env["x_allocated_technician_line_64c6d"].search(
            [
                ("x_studio_service_type_id", "=", self.x_studio_awb_service_type_id.id),
                ("x_studio_time_slot", "=", self.x_studio_time_slot),
                (
                    "x_allocated_technician_id.x_studio_user_id",
                    "in",
                    self.x_studio_area_id.x_studio_technicians.ids,
                ),
                (
                    "x_allocated_technician_id.x_studio_date",
                    "in",
                    date_list,
                ),

            ]
        )

        allocated_technician_schedule_ids = []
        for line in allocated_technician_line:
            allocated_sale_order = self.env["sale.order"].search(
                [
                    (
                        "x_studio_preferred_service_schedule",
                        "=",
                        line.x_allocated_technician_id.id,
                    ),
                    ("x_studio_awb_service_type_id", "=", line.x_studio_service_type_id.id),
                    ("x_studio_time_slot", "=", line.x_studio_time_slot),
                    ("state", "!=", "cancel"),
                ]
            )
            if self.env.context.get('active_id'):
                allocated_sale_order = allocated_sale_order.filtered(
                    lambda r: r.id != self.env.context.get('active_id')
                )

            available_allocation = line.x_studio_allocation - len(allocated_sale_order)
            if available_allocation > 0:
                allocated_technician_schedule_ids.append(line.x_allocated_technician_id.id)

        allocated_technician_schedule_recs = self.env["x_allocated_technician"].browse(allocated_technician_schedule_ids)
        user_ids = allocated_technician_schedule_recs.mapped('x_studio_user_id').ids
        related_user_recs = self.env["res.users"].browse(user_ids)
        partner_ids = related_user_recs.mapped('partner_id').ids
        priority_user_ids = []
        priority_partner_ids = []
        for user in user_ids:
            if self.env['res.users'].browse(user).partner_id.priority_asc:
                priority_user_ids.append(user)
        for x_id in user_ids:
            if x_id not in priority_user_ids:
                priority_user_ids.append(x_id)

        for partner in partner_ids:
            if self.env['res.partner'].browse(partner).priority_asc:
                priority_partner_ids.append(partner)
        for p_id in partner_ids:
            if p_id not in priority_partner_ids:
                priority_partner_ids.append(p_id)

        if self.x_studio_assigned_asc.id not in user_ids:
            self.x_studio_assigned_asc = False

        self.x_studio_assigned_asc_domain = json.dumps([("id", "in", priority_user_ids)])
        self.assigned_asc_sale_domain = json.dumps([("id", "in", priority_partner_ids)])

    @api.onchange('x_studio_area_id', 'x_studio_awb_service_type_id',
                  'x_studio_service_needed', 'x_studio_service_needed_1', 'x_studio_service_needed_2',
                  'x_studio_time_slot')
    def update_assigned_asc_field(self):
        if self.x_studio_awb_service_type_id.id and self.x_studio_area_id.id and self.x_studio_preferred_date and self.x_studio_time_slot:
            allocated_technician_line = self.env["x_allocated_technician_line_64c6d"].search(
                [
                    ("x_studio_service_type_id", "=", self.x_studio_awb_service_type_id.id),
                    ("x_studio_time_slot", "=", self.x_studio_time_slot),
                    (
                        "x_allocated_technician_id.x_studio_user_id",
                        "in",
                        self.x_studio_area_id.x_studio_technicians.ids,
                    ),
                    (
                        "x_allocated_technician_id.x_studio_date",
                        "=",
                        self.x_studio_preferred_date,
                    ),

                ]
            )

            if not allocated_technician_line:
                self.x_studio_assigned_asc = False

            allocated_technician_schedule_ids = []
            for line in allocated_technician_line:
                allocated_sale_order = self.env["sale.order"].search(
                    [
                        (
                            "x_studio_preferred_service_schedule",
                            "=",
                            line.x_allocated_technician_id.id,
                        ),
                        ("x_studio_awb_service_type_id", "=", line.x_studio_service_type_id.id),
                        ("x_studio_time_slot", "=", line.x_studio_time_slot),
                        ("state", "!=", "cancel"),
                    ]
                )
                if self.env.context.get("active_id"):
                    allocated_sale_order = allocated_sale_order.filtered(
                        lambda r: r.id != self.env.context.get("active_id")
                    )

                available_allocation = line.x_studio_allocation - len(allocated_sale_order)
                if available_allocation > 0:
                    allocated_technician_schedule_ids.append(line.x_allocated_technician_id.id)

            allocated_technician_schedule_recs = self.env["x_allocated_technician"].browse(allocated_technician_schedule_ids)
            user_ids = allocated_technician_schedule_recs.mapped('x_studio_user_id').ids
            related_user_recs = self.env["res.users"].browse(user_ids)
            partner_ids = related_user_recs.mapped('partner_id').ids
            priority_partner_ids = []
            priority_user_ids = []
            for user in user_ids:
                if self.env['res.users'].browse(user).partner_id.priority_asc:
                    priority_user_ids.append(user)
            for x_id in user_ids:
                if x_id not in priority_user_ids:
                    priority_user_ids.append(x_id)

            for partner in partner_ids:
                if self.env['res.partner'].browse(partner).priority_asc:
                    priority_partner_ids.append(partner)
            for p_id in partner_ids:
                if p_id not in priority_partner_ids:
                    priority_partner_ids.append(p_id)

            if user_ids:
                sale_rec = self.search([('x_studio_preferred_date', '=', self.x_studio_preferred_date)])
                count = self.search([], limit=1, order='id desc').assigned_asc_count
                if len(sale_rec) == 0:
                    self.x_studio_assigned_asc = priority_user_ids[count]
                    self.assigned_asc_count = count + 1
                elif sale_rec and (count < len(priority_user_ids)):
                    self.x_studio_assigned_asc = priority_user_ids[count]
                    self.assigned_asc_count = count + 1
                elif len(priority_user_ids) == count:
                    self.x_studio_assigned_asc = priority_user_ids[0]
                    self.assigned_asc_count = 1

            if partner_ids:
                sale_partner_rec = self.search([('x_studio_preferred_date', '=', self.x_studio_preferred_date)])
                count_partner = self.search([], limit=1, order='id desc').assigned_asc_count_partner
                if len(sale_partner_rec) == 0:
                    self.assigned_asc_sale = priority_partner_ids[count_partner]
                    self.assigned_asc_count_partner = count_partner + 1
                elif sale_partner_rec and (count_partner < len(priority_partner_ids)):
                    self.assigned_asc_sale = priority_partner_ids[count_partner]
                    self.assigned_asc_count_partner = count_partner + 1
                elif len(priority_partner_ids) == count_partner:
                    self.assigned_asc_sale = priority_partner_ids[0]
                    self.assigned_asc_count_partner = 1
