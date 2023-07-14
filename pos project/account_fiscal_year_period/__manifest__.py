# -*- coding: utf-8 -*-
{
    'name': "Account Fiscal Year Period",
    'summary': """
    Create periods Of Fiscal Year Per Month and quarter ,With Ability To Open/Close Each Month
    """,
    'description':
    """
        Create periods Of Fiscal Year Per Month and quarter, With Ability To Open/Close Each Month
    """,
    'author': "Apagen Solutions",
    'website': "www.apagen.com",
    'category': 'Accounting',
    'version': '15.0.1.1',
    'depends': ['account'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/account_fiscal_sequence.xml'
    ],
    'demo': [],
    "images":  ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
