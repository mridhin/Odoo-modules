# -*- coding: utf-8 -*-
{
    'name': 'Multiple Warehouses in Sale Order Lines',
    'version': '15.0',
    'category': 'Sales',
    'summary': 'Set warehouses per sale order lines.',
    'description': """This module will help to set warehouses per sale order 
                      lines and the picking will be created for the selected 
                      warehouses separately.""",
    'author': 'Achieve Without Borders, Inc.',
    'company': 'Achieve Without Borders, Inc.',
    'website': "http://www.achievewithoutborders.com",
    'depends': ['base', 'sale_management', 'account', 'stock'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
