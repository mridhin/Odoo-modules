# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError


class ProductCatalog(models.Model):
    _name = 'product.catalog'
    _description = "Product Catalog"

    name = fields.Char(string='Catalog Number', required=True,
                       copy=False, readonly=True, index=True, default=lambda self: _('New'))
    create_date = fields.Datetime(
        'Create Date', readonly=True, index=True, default=lambda self: fields.Datetime.now())
    attachment_name = fields.Char(
        'Catalog', compute='get_attachment_data')
    attachment = fields.Binary('Attachment', compute='get_attachment_data')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 index=True, default=lambda self: self.env.user.company_id)
    user_id = fields.Many2one('res.users', string='Users', index=True,
                              track_visibility='onchange', default=lambda self: self.env.user)

    def get_attachment_data(self):
        attachment_obj = self.env['ir.attachment']
        for emp in self:
            attachments = attachment_obj.search(
                [('res_id', '=', emp.id), ('res_model', '=', 'product.catalog')], limit=1)
            emp.attachment_name = attachments.name
            emp.attachment = attachments.datas

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'product.catalog') or _('New')
        result = super(ProductCatalog, self).create(vals)
        return result

    def send_by_email(self):
        self.ensure_one()
        attachment_obj = self.env['ir.attachment']
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                "awb_product_catalog_generator", 'email_template_edi_product_catalog')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        attachments = attachment_obj.search(
            [('res_id', '=', self.id), ('res_model', '=', 'product.catalog')], limit=1)
        ctx = {
            'default_model': 'product.catalog',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', True),
            'force_email': True,
            'default_attachment_ids': [(6, 0, attachments.ids)],
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
