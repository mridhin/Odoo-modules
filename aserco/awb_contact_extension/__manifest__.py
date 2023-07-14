# -*- coding: utf-8 -*-

{
    'name': """AWB Contact Extension""",
    'summary': '''AWB Contact Extension''',
    'version': '15.0.1.0.0',
    'category': 'website',
    'summary': 'AWB Contact Extension',
    'website': 'https://www.achievewithoutborders.com/',
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',
    'description': """
       AWB Contact Extension
    """,
    'depends': ['base', 'contacts'],

    'data': [
        'security/ir.model.access.csv',
        'views/con_extension.xml',
        'views/service_offered.xml',
        'views/contact_views.xml'
    ],
    'assets': {
        'web.assets_frontend': [

        ],
        'web.assets_qweb': [

        ],
    },

    # 'currency': 'EUR',
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
