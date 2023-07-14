# -*- coding: utf-8 -*-
{
    'name': "Philippine Barangays",
    'version': '15.0.1.0.3',
    'summary': """
        Philippine Barangays
        """,
    'description': """
        Philippine Barangays
    """,
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Localization',

    # any module necessary for this one to work correctly
    'depends': ['website_sale','contacts','mail','base_address_city'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ph_city_views.xml',
        'views/res_partner_views.xml',
        'views/ph_barangay_view.xml',
        'views/website_sale_template.xml',
        'views/help_page.xml',
        'wizard/provience_help_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'assets':{
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
            '/philippine_barangays/static/src/js/website_sale_address.js'
        ],
    },
    'post_init_hook': 'add_philippines_state_city_barangay',
    'license': 'LGPL-3',
}