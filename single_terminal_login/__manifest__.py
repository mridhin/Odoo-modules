# -*- coding: utf-8 -*-
{
    'name': 'Single terminal Login on Single Device',
    'summary': "Single Terminal Login on Single Device",
    'description': "Single Terminal Login on Single Device",

    'author': '',
    'website': '',
    'support': '',

    'category': 'Extra Tools',
    'version': '13.0.0.0',
    'depends': ['web'],

    'data': [
        'security/restrict_user_security.xml',
        'security/ir.model.access.csv',
        'data/login_user_find.xml',
        'views/res_users.xml',
    ],

    'license': "OPL-1",
    'price': 200,
    'currency': "EUR",

    'auto_install': False,
    'installable': True,

    'images': [''],
}
