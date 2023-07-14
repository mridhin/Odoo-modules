# -*- coding: utf-8 -*-
{
    'name': "POS Sale User System Restriction",
    'summary': """
        AWB POS Sale User System Restriction""",
    'description': """
        Extension Odoo Apps
    """,
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'category': 'POS',
    'version': '15.0.1',
    'depends': ['base', 'point_of_sale', 'awb_void_orders'],
    'data': [
        'views/res_users.xml',
    ],
}
