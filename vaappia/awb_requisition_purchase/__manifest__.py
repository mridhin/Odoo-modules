# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Purchase Requisition",

    'summary': """
        Purchase Requisition
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '15.0.1.1.1',

    'depends': ['approvals_purchase','purchase_requisition', 'purchase', 'stock', 'purchase_stock'],

    'data': [
        'views/hr_employee_views.xml',
        'views/approval_category_approver_views.xml',
        'views/approval_request_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
