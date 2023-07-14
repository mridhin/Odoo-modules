# -*- coding: utf-8 -*-
{
    'name': "AWB Smart Suite SMS Gateway Integration",

    'summary': """AWB Smart Suite SMS Gateway Integration""",

    'description': """
        Overrides the default Odoo IAP SMS gateway. Use the Smart Suite gateway instead.
    """,

    'license': 'LGPL-3',
    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'SMS',
    'version': '15.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['sms','project'],

    # always loaded
    'data': [
        'views/res_config_settings.xml',
        'views/sms_template.xml',
    ],
}
