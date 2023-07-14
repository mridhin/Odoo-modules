# -*- coding: utf-8 -*-
{
    'name': "Philippine Tax App",
    'summary': """ Philippine Tax App """,
    'description': """ Philippine Tax App """,
    'author': "Apagen Solutions",
    'website': "www.apagen.com",
    'category': 'Accounting',
    'version': '15.0.1.1',
    'depends': ['web', 'account', 'l10n_generic_coa', 'purchase', 'sale_management', 'account_fiscal_year_period'],
    'data': [
        'security/philippine_category_security.xml',
        'security/awb_philippine_tax_app_security.xml',
        'security/ir.model.access.csv',
        'data/tax_property_data.xml',
        'data/industry_covered_vat_data.xml',
        'data/account_account_data.xml',
        'data/account_tax_data.xml',
        'data/report_paperformat_data.xml',
        'wizard/wizard_sales_relief_reports.xml',
        'wizard/wizard_purchase_relief_reports.xml',
        'report/reorts_relief_view.xml',
        'report/m_2550_report_template.xml',
        'report/q_2550_report_template.xml',
        'report/e_0619_report_template.xml',
        'report/eq_1601_report_template.xml',
        'report/e_1604_report_template.xml',
        'report/2307_report_template.xml',
        # 'views/assets.xml',
        'views/tax_property_view.xml',
        'views/account_tax_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/industry_covered_vat_view.xml',
        #'views/account_payment_view.xml',
        'views/m_2550_view.xml',
        'views/q_2550_view.xml',
        'views/e_0619_view.xml',
        'views/eq_1601_view.xml',
        'views/e_1604_view.xml',
        'views/e_2307_view.xml',
        # 'report/report_invoice.xml',
    ],
    'assets': {
        "web.assets_backend": [
            "awb_philippine_tax_app/static/src/css/account.css",
        ],
        "web.report_assets_common": [
            "awb_philippine_tax_app/static/src/css/**/*",
        ],
        "web.assets_qweb": [
            "awb_philippine_tax_app/static/src/**/*",
        ],
    },

    'installable': True,
    'application': True,
    "auto_install": False,
}
