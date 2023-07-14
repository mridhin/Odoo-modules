# -*- coding: utf-8 -*-
{
    'name': "AWB Rating Custom",

    'summary': """Customized Rating Module""",

    'license': 'LGPL-3',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",
    'category': 'Services/Field Service',
    'version': '15.0.0.2',
    'depends': [
        'portal', 'rating',
    ],
    'data': [
        'views/rating_template_views.xml'
    ],
    'assets': {
        'web.assets_frontend': [
                'awb_rating_custom/static/src/css/rate.scss',
        ]
    },

    'images': ['static/description/icon.png'],
}
