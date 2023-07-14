# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import datetime
import json


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_new_quotation(self):
        action = super(CrmLead, self).action_new_quotation()
        teritory = self.env['x_territory'].search([('x_name', '=', self.x_studio_province.name)], limit=1)
        action['context'].update({
            'default_x_studio_area_id': teritory.id,
            'default_x_studio_source_of_booking': self.x_studio_source_of_booking,
            'default_x_studio_awb_service_type_id': self.x_studio_awb_service_type_id.id,
            'default_x_studio_preferred_date': self.service_date,
            'default_x_studio_time_slot': self.x_studio_preferred_time_slot,
        })
        # action['context']['default_x_studio_area_id'] = teritory.id,
        # action['context']['default_x_studio_preferred_date'] = self.service_date,
        # action['context']['default_x_studio_time_slot'] = self.x_studio_preferred_time_slot,
        print(action['context'], self.x_studio_source_of_booking)
        return action

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super(CrmLead, self)._prepare_customer_values(partner_name, is_company, parent_id)
        res['first_name'] = self.first_name
        res['last_name'] = self.last_name
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # The onchange function is equal to the following automated action (Filter "Available Service Schedule" field)
    @api.onchange('x_studio_preferred_date')
    def _onchange_service_date(self):
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
                # (
                #     "x_allocated_technician_id.x_studio_date",
                #     "in",
                #     date_list,
                # ),

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
            if self.env.context["active_id"]:
                allocated_sale_order = allocated_sale_order.filtered(
                    lambda r: r.id != self.env.context["active_id"]
                )

            available_allocation = line.x_studio_allocation - len(allocated_sale_order)
            if available_allocation > 0 and line.x_allocated_technician_id.x_studio_user_id.id == self.x_studio_assigned_asc.id:
                allocated_technician_schedule_ids.append(line.x_allocated_technician_id.id)

        if (
                self["x_studio_preferred_service_schedule"].id
                not in allocated_technician_schedule_ids
        ):
            self["x_studio_preferred_service_schedule"] = False

        self["x_studio_available_service_schedule_domain"] = json.dumps(
            [("id", "in", allocated_technician_schedule_ids)]
        )

    @api.onchange('x_studio_awb_service_type_id')
    def _onchange_area_domain(self):
        allocated_technician_line_64c6d = self.env['x_allocated_technician_line_64c6d']
        allocated_technician_line_64c6d = allocated_technician_line_64c6d.search(
            [('x_studio_service_type_id', '=', self.x_studio_awb_service_type_id.id)])
        users = allocated_technician_line_64c6d.mapped("x_allocated_technician_id.x_studio_user_id")
        territories = self.env['x_territory'].search([('x_studio_technicians', 'in', users.ids)])
        area = territories.ids
        if self["x_studio_area_id"].id not in area:
            self["x_studio_area_id"] = False
        self["x_studio_area_domain"] = json.dumps([('id', 'in', area)])
