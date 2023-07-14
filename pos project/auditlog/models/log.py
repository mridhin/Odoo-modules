# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import _, api, fields, models
from datetime import date
from odoo.exceptions import UserError 

# from pip._vendor.pygments.lexer import _inherit


class AuditlogLog(models.Model):
    _name = "auditlog.log"
    _description = "Auditlog - Log"
    _order = "create_date desc"

    name = fields.Char("Resource Name", size=64)
    model_id = fields.Many2one(
        "ir.model", string="Model", index=True, ondelete="set null"
    )
    model_name = fields.Char(readonly=True)
    model_model = fields.Char(string="Technical Model Name", readonly=True)
    res_id = fields.Integer("Resource ID")
    user_id = fields.Many2one("res.users", string="User")
    method = fields.Char(size=64)
    line_ids = fields.One2many("auditlog.log.line", "log_id", string="Fields updated")
    http_session_id = fields.Many2one(
        "auditlog.http.session", string="Session", index=True
    )
    http_request_id = fields.Many2one(
        "auditlog.http.request", string="HTTP Request", index=True
    )
    log_type = fields.Selection(
        [("full", "Full log"), ("fast", "Fast log")], string="Type"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Insert model_name and model_model field values upon creation."""
        for vals in vals_list:
            if not vals.get("model_id"):
                raise UserError(_("No model defined to create log."))
            model = self.env["ir.model"].sudo().browse(vals["model_id"])
            vals.update({"model_name": model.name, "model_model": model.model})
        return super().create(vals_list)

    def write(self, vals):
        """Update model_name and model_model field values to reflect model_id
        changes."""
        if "model_id" in vals:
            if not vals["model_id"]:
                raise UserError(_("The field 'model_id' cannot be empty."))
            model = self.env["ir.model"].sudo().browse(vals["model_id"])
            vals.update({"model_name": model.name, "model_model": model.model})
        return super().write(vals)

    def print_log(self, model, props,action_name):
        if not model == 'auditlog.log' :
            lines = []
            account_id = self.env[model].search([('id','=',props)])

            model_name = self.env['ir.model'].search([('model','=',model)])
            if model_name.model == 'cc_x_reading.x_reading':
                name = account_id.reference
            elif model_name.model == 'cc_z_reading.z_reading':
                name = account_id.reference
            else:
                name = account_id.name
            field_id = self.env['ir.model.fields'].search([('model_id','=',model_name.id)])
            field_name_id = ''
            for id in field_id:
                description = id.field_description
                if description == 'Display Name':
                    field_name_id = id                   
            print_id = self.env['auditlog.log'].create({'create_date':date.today(),
                                                       'user_id': self.env.uid,
                                                        'method':'write',
                                                        'res_id':account_id.id,
                                                        'name':name,
                                                       'model_id':model_name.id
                                                          })
            line={'create_date':date.today(),
                    'field_description':'Main Attachment',
                    'old_value_text': '',
                    'new_value_text': action_name,
                    'field_id':field_name_id.id,}
            lines.append((0,0, line))
       
        
        
        
class AuditlogLogLine(models.Model):
    _name = "auditlog.log.line"
    _description = "Auditlog - Log details (fields updated)"

    field_id = fields.Many2one(
        "ir.model.fields", ondelete="set null", string="Field", index=True
    )
    log_id = fields.Many2one(
        "auditlog.log", string="Log", ondelete="cascade", index=True
    )
    old_value = fields.Text()
    new_value = fields.Text()
    old_value_text = fields.Text("Old value Text")
    new_value_text = fields.Text("New value Text")
    field_name = fields.Char("Technical name", readonly=True)
    field_description = fields.Char("Description", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure field_id is not empty on creation and store field_name and
        field_description."""
        for vals in vals_list:
            if not vals.get("field_id"):
                raise UserError(_("No field defined to create line."))
            field = self.env["ir.model.fields"].sudo().browse(vals["field_id"])
            vals.update(
                {"field_name": field.name, "field_description": field.field_description}
            )
        return super().create(vals_list)

    def write(self, vals):
        """Ensure field_id is set during write and update field_name and
        field_description values."""
        if "field_id" in vals:
            if not vals["field_id"]:
                raise UserError(_("The field 'field_id' cannot be empty."))
            field = self.env["ir.model.fields"].sudo().browse(vals["field_id"])
            vals.update(
                {"field_name": field.name, "field_description": field.field_description}
            )
        return super().write(vals)
    
    
    
    
