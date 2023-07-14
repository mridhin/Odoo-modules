# -*- coding: utf-8 -*-
{
    "name": "AWB Custom Invoices and Receipts",
    "summary": "AWB Custom Invoices and Receipts",
    "description": """
        AWB Custom Invoices and Receipts
    """,
    "author": "Achieve Without Borders, Inc.",
    "website": "https://www.achievewithoutborders.com/page/odoo",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Localization",
    "version": "16.0.0.0",
    # any module necessary for this one to work correctly
    "depends": [
        # "awb_l10n_ph_pos",
        "awb_common",
        "sale",
        "sale_management",
        "stock",
        "l10n_ph",
        "cc_custom_account",
        "account",
    ],
    # always loaded
    'data': [
        'views/report_invoice.xml',
        'views/report_templates.xml',
        'reports/awb_custom_external_layout.xml',
        'views/account_move_views.xml',
        'views/res_company.xml',
        'views/res_partner_views.xml',
        'views/report_payment_receipt_templates.xml',
        'views/account_report.xml',
        'views/account_journal.xml'
    ],
}
