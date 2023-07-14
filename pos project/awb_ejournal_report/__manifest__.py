# -*- coding: utf-8 -*-

{
    'name': """AWB eJournal Report""",
    'summary': '''E-journal records all sales per terminal per branch location''',
    'version': '15.0.1.0.3',
    'category': 'Point of Sale',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',
    'depends': ['base', 'point_of_sale', 'awb_l10n_ph_pos'],
    'data': [
            'security/pos_security.xml',
            'security/ir.model.access.csv',
            'views/ejournal_report_view.xml',
            'reports/ejournal_report_template.xml',
            'reports/ejournal_text_template.xml',
            'reports/ejournal_receipt_view.xml',
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}
