# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Preprinted Checks",
    'summary': """
        AWB Preprinted Checks
        """,
    'description': """
        AWB Preprinted Checks
    """,
    'author': "Achieve Without Borders, Inc",
    'website': "http://www.achievewithoutborders.com",
    'category': 'Accounting',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['sale', 'account'],
    'data': [
        'reports/awb/report_actions.xml',
        'reports/awb/report_format_awb.xml',
        'reports/awb/awb_preprinted_checks.xml',
        'views/account_payment_view.xml'

    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
