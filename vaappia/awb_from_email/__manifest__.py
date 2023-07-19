# -*- coding: utf-8 -*-
{
    'name': "AWB From Email Integration",

    'summary': """AWB From Email Integration""",

    'description': """
        Overrides the default Odoo From Email and will use system parameters from email.
    """,

    'license': 'LGPL-3',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    'category': 'Mail',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'views/res_config_settings.xml',
    ],
}
