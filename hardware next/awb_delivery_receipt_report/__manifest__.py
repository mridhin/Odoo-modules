# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Delivery Receipt",
    'summary': """
        AWB Delivery Receipt
        """,
    'description': """
        AWB Delivery Receipt
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': "Delivery Receipt",
    'version': '15.0.1.0.0',
    'depends': ['base','stock'],
    'data': [
            'views/stock_picking.xml',
            'report/report_delivery.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
