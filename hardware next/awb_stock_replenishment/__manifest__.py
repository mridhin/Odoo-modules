# -*- coding: utf-8 -*-
{
    'name': 'AWB Stock Replenishment',
    'version': '15.0.0.1', 
    'category': 'Stock ',
    'summary': 'Stock Replenishment',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    "license": "LGPL-3",
    'description': """
  Stock Replenishment
    """,
    'depends': ['base','stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_replenishment_location.xml',
        'views/stock_warehouse_orderpoint.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
