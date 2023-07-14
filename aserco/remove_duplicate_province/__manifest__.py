# -*- coding: utf-8 -*-
{
    'name': "Remove Duplicate Province",
    'version': '15.0.1.0.0',
    'summary': """
        Remove Duplicate Province
        """,
    'description': """
        Remove Duplicate Province,
        Remove Number and Special Character from City
    """,
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Localization',

    # any module necessary for this one to work correctly
    'depends': ['philippine_barangays'],

    # always loaded
    'data': [
            'data/ir_cron_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'assets':{
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
        ],
    },
    'license': 'LGPL-3',
    'auto_install': False,
    'installable': True,
    'application': False,
}