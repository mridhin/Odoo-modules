# -*- coding: utf-8 -*-

import base64
from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductCatalogWizard(models.TransientModel):
    _name = 'product.catalog.wizard'
    _description = "Product Catalog Wizard"
    
    @api.onchange('catalog_type')
    def _onchange_catalog_type(self):
        if self.catalog_type == 'product':
            self.categories_ids = False
        else:
            self.product_ids = False


    catalog_type = fields.Selection(
        [('product', 'Product'), ('category', 'Category')],
        string='Catalog Type',
        default='product')
    product_ids = fields.Many2many('product.product', string="Products")
    categories_ids = fields.Many2many('product.category', string="Categories")
    image_size = fields.Selection(
        [('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        string='Image Size',
        default='small')
    user_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self.env.user)
    company_id = fields.Many2one(
        'res.company', string="company", default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', string="Currency", default=lambda x: x.env.company.currency_id)
    price = fields.Boolean(default=True, string="Price")
    report_style = fields.Selection(
        [('style_1', 'Style 1'),
         ('style_2', 'Style 2'),
         ('style_3', 'Style 3'),
         ('style_4', 'Style 4'),
         ('style_5', 'Style 5')],
        string='Style',
        default='style_1')
    description = fields.Boolean(default=True, string="Description")
    print_box_per_row = fields.Selection(
        [('two_box_per_row', '2 box per row'),
         ('three_box_per_row', '3 box per row'),
         ('four_box_per_row', '4 box per row')],
        string='Print box per row',
        default='two_box_per_row')

    def print_style_catalog(self):
        Attachments = self.env['ir.attachment']
        product_catalog_obj = self.env['product.catalog']
        
        data = {'ids': []}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        if self.report_style in ['style_1', 'style_3']:
            action = self.env.ref('awb_product_catalog_generator.action_report_product_catalog_1_3').\
                report_action(self, data=data)
        else:        
            action = self.env.ref('awb_product_catalog_generator.action_report_product_catalog').\
                report_action(self, data=data)

        action.update({'close_on_report_download': False})
    
        product_catalog_id = product_catalog_obj.create({
            'create_date': fields.Datetime.now()
        })
        
        if self.report_style in ['style_1', 'style_3']:
            product_catalog_pdf = self.env.ref('awb_product_catalog_generator.action_report_product_catalog_1_3')._render_qweb_pdf(
            product_catalog_id.id, data=data)[0]
        else:        
            product_catalog_pdf = self.env.ref('awb_product_catalog_generator.action_report_product_catalog')._render_qweb_pdf(
            product_catalog_id.id, data=data)[0]

        Attachments.sudo().create({
            'name': 'product_catalog_report_%s.pdf' % self.report_style,
            'datas': base64.b64encode(product_catalog_pdf),
            'res_model': 'product.catalog',
            'res_id': product_catalog_id.id,
            'mimetype': 'application/pdf',
            'type': 'binary',
        })
        return action