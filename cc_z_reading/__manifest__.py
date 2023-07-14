# -*- coding: utf-8 -*-
{
    'name': "Z-Reading Module",

    'summary': "Z-Reading Module",

    'description': """
        Adds Z-Reading to POS App
    """,

    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '16.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'point_of_sale',
        'cc_custom_account',
        'pos_sale_receipt',
        'awb_l10n_ph_pos',

    ],
    # always loaded
    'data': [
        'data/ir.model.access.csv',
        'reports/z_reading_reports.xml',
        'views/z_reading_reporting_menus.xml',
        'views/z_reading_report_templates.xml',
        'views/z_reading_views.xml',
    ],

}

