# -*- coding: utf-8 -*-
# Copyright (c) 2022 Achieve Without Borders, Inc. (<http://www.achievewithoutborders.com>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
{
    'name': 'Sales Multiple Discount',
    'version': '15.0.0.0',
    'category': 'Others',
    'summary': 'Sales Multiple Discount',
    'description': """
        Sales Multiple Discount
    """,
    'author': 'Achieve Without Borders, Inc.',
    'website': "http://www.achievewithoutborders.com",
    'company': 'Achieve Without Borders, Inc.',
    'depends': ['base', 'product', 'sale', 'sale_management', 'stock', 'awb_multi_discount'],
    'data': [
        'views/sale_order_view.xml',
        'reports/sale_order.xml',
    ],
    'qweb': [],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
