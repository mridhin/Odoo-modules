# -*- coding: utf-8 -*-
{
    'name': "web_maintenance_request",

    'summary': """
        Give users the option to create maintenance requests from a website and receive an email upon successful completion of the request """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Ridhin",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'hr_maintenance', 'mail'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/mail_view.xml'
    ],
}
