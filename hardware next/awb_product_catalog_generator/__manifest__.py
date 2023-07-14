# -*- coding: utf-8 -*-
{
    'name': "Custom Sale Report",
    'summary': "",
    'description': """Custom Sale Report pivot""",
    'category': 'Sale Order',
    'version': '15.0.0.0',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/awb_email_catalog.xml',
        'views/product_catalog_views.xml',
        'wizard/product_catalog_wizard_views.xml',
        'reports/product_catalog_report.xml',
        'reports/product_catalog_report_template.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}