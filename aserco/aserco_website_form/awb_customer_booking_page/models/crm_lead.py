from odoo import api, fields, models, _
from datetime import date


class CrmLead(models.Model):
    _inherit = "crm.lead"

    barangay = fields.Char(string="Barangay")
    appointment_type = fields.Many2one('calendar.appointment.type', string="Service Needed")
    prefer_time_slot = fields.Selection([('am', "AM"), ('pm', 'PM')], string="Preferred Time Slot")
    first_name = fields.Char(string="First name")
    last_name = fields.Char(string="Last name")
    service_date = fields.Date('Preferred Service Date')

    @api.onchange('service_date')
    def _onchange_service_date(self):
        if self.service_date and self.service_date < fields.Date.today():
            self.service_date = False

    # @api.constrains('service_date')
    # def _check_service_date(self):
    #     for record in self:
    #         if record.service_date and record.service_date < date.today():
    #             raise models.ValidationError("Preferred Service are not allowed.")
