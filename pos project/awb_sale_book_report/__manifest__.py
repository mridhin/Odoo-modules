# -*- coding: utf-8 -*-

{
    'name': """AWB Sales Book Report""",
    'summary': '''AWB Sales Book Report''',
    'version': '15.0.1.0.1',
    'category': 'Point of Sale',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',
    'depends': ['base','point_of_sale','awb_l10n_ph_pos'],
    'data': [
           'security/ir.model.access.csv',
           'views/sale_report_view.xml',
           'reports/sale_report_template.xml',  
           'reports/sale_receipt.xml',   
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}
