# -*- coding: utf-8 -*-
{
    'name': "POS Sale Receipt",

    'summary': """
        AWB POS & sale receipt """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'category': 'Localization',
    'version': '15.0.1.0.1',

    'depends': ['base', 'point_of_sale', 'sale_management', 'account', 'cc_custom_account', 'awb_common', 'pos_sale'],

    'data': [
        'security/ir.model.access.csv',
        'data/sale_team_prefix_data.xml',
        'views/crm_team_views.xml',
        'views/sale_order_views.xml',
        'views/pos_config.xml',
        'views/account_move_views.xml',
    ],
    # point_of_sale.assets added
    'assets': {
        'point_of_sale.assets': [
            'pos_sale_receipt/static/src/js/model.js',
            'pos_sale_receipt/static/src/js/sale_order_form_view.js',
            'pos_sale_receipt/static/src/css/sale_order_button.css',
        ],
    },
}
