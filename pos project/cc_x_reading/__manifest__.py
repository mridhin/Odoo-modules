# -*- coding: utf-8 -*-
{
    'name': "X-Reading Module",

    'summary': "X-Reading Module",

    'description': """
        Adds X-Reading to POS App
    """,

    'author': "Achieve Without Borders, Inc.",
    'website': "https://www.achievewithoutborders.com/page/odoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '15.0.13.2',

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
        'data/sequence_data_x_reading.xml',
        'data/sequence_data_pos_report.xml',
        'security/security.xml',
        'reports/x_reading_reports.xml',
        # 'views/x_reading_reporting_menus.xml',
        'views/x_reading_report_templates.xml',
        'views/x_reading_views.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'cc_x_reading/static/js/PopUps/clossingSessionPopUps.js',
        ],
    }
}

