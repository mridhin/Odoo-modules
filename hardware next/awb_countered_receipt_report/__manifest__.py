# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Countered Receipt Report",
    'summary': """
        AWB Countered Receipt Report
        """,
    'description': """
        AWB Countered Receipt Report
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': "Operations/Expense",
    'version': '15.0.1.0.0',
    'depends': ['base','account','web','account_accountant'],
    'data': [
            'views/account_payment_report.xml',
            'report/report_countered_receipt_template.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
