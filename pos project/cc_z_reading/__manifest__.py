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
        'data/sequence_data_z_reading.xml',
        'data/sequence_data_pos_report.xml',
        'security/security.xml',
        'reports/z_reading_reports.xml',
        'views/z_reading_reporting_menus.xml',
        'views/z_reading_report_templates.xml',
        'views/z_reading_views.xml',
        'views/pos_report_views.xml',
        'views/pos_config_view.xml',
        'views/pos_session_view.xml',
    ],

    'assets': {
        'point_of_sale.assets': [
            'cc_z_reading/static/src/css/pos.css',
            'cc_z_reading/static/js/PopUps/clossingSessionPopUps.js',
        ],
        'web.assets_qweb': [
            'cc_z_reading/static/src/xml/Popups/ClosePosPopup.xml',
        ]
    }
}
