# -*- coding: utf-8 -*-

{
    'name': 'AWB POS Service Charge',
    'version': '15.0.1',
    'category': 'POS',
    'sequence': 356,
    'summary': 'POS Service Charge',
    'description': """POS Service Charge""",

    'author': 'AWB',
    'website': '',

    'depends': ['point_of_sale'],
    'data': [
        'views/pos_terminal_views.xml',
        'views/pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'awb_pos_service_charge/static/src/js/pos_buttons.js',
            'awb_pos_service_charge/static/src/js/service_popup.js',
            'awb_pos_service_charge/static/src/js/models.js',
            'awb_pos_service_charge/static/src/js/ProductsWidget.js',
            'awb_pos_service_charge/static/src/js/ProductScreen.js',
            'awb_pos_service_charge/static/src/js/OrderWidget.js',
        ],
        'web.assets_qweb': [
            'awb_pos_service_charge/static/src/xml/service_popup.xml',
            'awb_pos_service_charge/static/src/xml/pos_buttons.xml',
            'awb_pos_service_charge/static/src/xml/OrderWidget.xml',
        ],
    },
    
    'application': True,
    'license': 'LGPL-3'
}
