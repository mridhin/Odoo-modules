# -*- coding: utf-8 -*-
{
    'name': "Rdian Software",

    'summary': """
        Ordering System For Fastag""",

    'description': """

    """,

    'author': "Redian Software",
    'website': "https://www.rediansoftware.com/",

    'category': 'Inventory',
    'version': '14.0.1',
    'sequence': '-101',

    # any module necessary for this one to work correctly
    'depends': ['base', 'rn_vehical_class'],

    # always loaded
    'data': ['security/ir.model.access.csv',
             'security/rule.xml',
             'views/views.xml',
             'data/sequence.xml',
             ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
