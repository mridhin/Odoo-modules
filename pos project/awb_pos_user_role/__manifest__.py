# -*- coding: utf-8 -*-

{
    'name': """AWB POS User Matrix""",
    'summary': '''POS user role for Cashier, Supervisor, Accountant and Administrator''',
    'version': '15.0.1.0.1',
    'category': 'Point of Sale',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',
    'depends': ['base','point_of_sale'],
    'data': [
           'security/pos_security.xml',
           'security/ir.model.access.csv',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
