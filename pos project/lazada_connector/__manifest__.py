# -*- coding: utf-8 -*-
{
    'name': 'AWB Lazada Connector',
    'version': '15.0.0.1', 
    'category': 'Sales ',
    'summary': 'Lazada Connector module to sync with Lazada and Odoo',
    'website': '',
    'author': 'Acheive Without Borders',
    "license": "LGPL-3",
    'description': """
    Lazada Connector module to sync with Lazada and Odoo
    """,
    'depends': ['base','mail','sale','stock','sale_stock','product_dimension','product_brand'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/lazada_product_sync.xml',
        'wizard/lazada_order_sync.xml',
        'views/lazada_connector_views.xml',
        'views/lazada_payment_methods.xml',
        'views/lazada_category.xml',
        'views/product_brand.xml',
        'views/sale_order.xml',
        'views/product_template_views.xml'
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
