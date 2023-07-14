# -*- coding: utf-8 -*-
{
    'name': "POS Signature",

    'summary': """
        POS Order Signature """,

    'description': """
        it will allow u to sign in the POS
    """,

    'author': "awb-Tony",

    'category': 'Localization',
    'version': '15.0.1',

    'depends': ['point_of_sale'],

    'data': [
        'views/pos_config_settings.xml',
        'views/pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'sh_pos_order_signature/static/src/js/action_button.js',
            'sh_pos_order_signature/static/src/js/models.js',
            'sh_pos_order_signature/static/src/js/popup.js',
            'sh_pos_order_signature/static/src/lib/jSignature.min.js',
            'sh_pos_order_signature/static/src/css/pos.css',

        ],
        'web.assets_qweb': [
            'sh_pos_order_signature/static/src/xml/action_button.xml',
            'sh_pos_order_signature/static/src/xml/popup.xml',
            'sh_pos_order_signature/static/src/xml/receipt.xml',
        ]

    },
}