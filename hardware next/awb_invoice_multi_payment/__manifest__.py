# -*- coding: utf-8 -*-
{
    'name': "Invoice Multi Payment",
    'summary': "select multiple invoices under same partner and generate draft payment",
    'description': """
        select multiple invoices under same partner and generate draft payment
    """,
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.5',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/",
    'depends': ['account'],
    'data': [
        'views/account_payment_view.xml',
    ],
    'demo': [
    ],
    'application': False,
    'auto_install': False,
    'installable': True,
    'license': 'LGPL-3',
}