# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Payment Countered Receipt",
    'summary': """
        AWB Payment Countered Receipt
        """,
    'description': """
        AWB Payment Countered Receipt
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': "Operations/Expense",
    'version': '15.0.1.0.0',
    'depends': ['base','account'],
    'data': [
            'views/account_payment.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
