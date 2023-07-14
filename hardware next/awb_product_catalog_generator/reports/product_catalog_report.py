# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
from odoo import models, api, fields
from odoo.tools import pycompat, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_round


class ProductCatalogReportStyle1(models.AbstractModel):
    _name = 'report.awb_product_catalog_generator.report_product_catalog'
    _description = 'Product Catalog Report Style'

    def _get_product_details(self, data):
        category_ids = data.get('category_ids')
        filter_type = data.get('filter_type')
        product_ids = data.get('product_ids')
        if filter_type == 'category':
            product_ids = self.env['product.product'].search(
                [('categ_id', 'child_of', category_ids.ids)])
        else:
            product_ids = self.env['product.product'].search(
                [('id', 'in', product_ids.ids)])
        return product_ids

    def _get_product_link(self, product):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        website_url = str(base_url) + "/shop/product/" + \
            str(product.product_tmpl_id.id)
        return website_url

    @api.model
    def _get_report_values(self, docids, data=None):
        filter_type = data['form']['catalog_type']
        category_ids = self.env['product.category'].browse(
            data['form']['categories_ids'])
        product_ids = self.env['product.product'].browse(
            data['form']['product_ids'])
        if data['form'].get('currency_id'):
            currency_id = self.env['res.currency'].browse(
                data['form']['currency_id'][0])
        else:
            currency_id = False

        price_check = data['form']['price']
        image_size = data['form']['image_size']
        report_style = data['form']['report_style']
        description_check = data['form']['description']
        print_box_per_row = data['form']['print_box_per_row']
        report_style = data['form']['report_style']
        data = {
            'filter_type': filter_type,
            'product_ids': product_ids,
            'category_ids': category_ids,
            'currency_id': currency_id,
            'price_check': price_check,
            'image_size': image_size,
            'report_style': report_style,
            'description_check': description_check,
            'print_box_per_row': print_box_per_row,
            'company': self.env.user.company_id,
            'company_id': self.env.user.company_id,
        }
        docargs = {
            'doc_model': 'product.catalog',
            'data': data,
            'get_product_details': self._get_product_details,
            'get_product_link': self._get_product_link,
            'company_id': self.env.user.company_id,
            'company': self.env.user.company_id,
        }
        return docargs
