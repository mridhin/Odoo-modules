# -*- coding: utf-8 -*-
{
    'name': 'AWB Customer Testimonial',
    'version': '15.0.0.1', 
    'category': 'Website',
    'summary': 'AWB Customer Testimonial',
    'website': 'https://www.achievewithoutborders.com/',
    'author': 'Achieve Without Borders',
    "license": "LGPL-3",
    'description': """
    AWB Customer Testimonial
    """,
    'depends': ['website','portal_rating'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_customer_testimonials.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'awb_customer_testimonial/static/src/css/rating.css',
            'awb_customer_testimonial/static/src/js/rating.js',
        ],
    },
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
