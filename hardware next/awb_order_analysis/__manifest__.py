# -*- coding: utf-8 -*-
{
    'name': 'AWB Order Analysis',
    'version': '15.0.0.1', 
    'category': 'Purchase ',
    'summary': 'Order Analysis',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    "license": "LGPL-3",
    'description': """
   Order Analysis
    """,
    'depends': ['base','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_analysis.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
