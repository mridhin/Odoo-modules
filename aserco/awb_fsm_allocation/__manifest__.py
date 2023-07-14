# -*- coding: utf-8 -*-
{
    'name': "AWB FSM Allocation",
    'description': """
        FSM Allocation
    """,
    'license': 'LGPL-3',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['sale', 'contacts', 'industry_fsm'],

    'data': [
        'security/ir.model.access.csv',
        'views/contact_view.xml',
        'views/sale_order_views.xml',
        'views/users_view.xml',
        'views/awb_city.xml',
        'views/territory.xml',
    ],
}
