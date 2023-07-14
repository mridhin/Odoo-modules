# -*- coding: utf-8 -*-
{
    'name': "AWB Customer Booking Page",
    'version': '15.0.1.0.7',
    'category': 'Website',
    'summary': 'AWB Customer Booking Page',
    'website': 'https://www.achievewithoutborders.com/',
    'author': 'Achieve Without Borders',
    "license": "LGPL-3",
    'description': """
    AWB Aserco Customer Booking Page
    """,
    'depends': ['website','crm'],
    'data': [
        'views/templates.xml',
        'views/crm_lead_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'awb_customer_booking_page/static/src/css/rating.css',
            'awb_customer_booking_page/static/src/js/rating.js',
        ],
    },
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
