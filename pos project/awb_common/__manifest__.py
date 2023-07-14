# -*- coding: utf-8 -*-
{
    "name": "AWB Common Fields",
    "summary": "AWB Common Fields for POS and BIR CAS",
    "description": """
        This module contains the common fields for POS and BIR CAS.
    """,
    "author": "Achieve Without Borders, Inc.",
    "website": "https://www.achievewithoutborders.com/page/odoo",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Localization",
    "version": "15.0.0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "sale",
        "account_accountant",
    ],
    # always loaded
    'data': [
        'views/account_move_views.xml',  #originally from pos_sale_receipt
        'views/res_company.xml',  #originally from awb_l10n_ph_pos
        'views/pos_config.xml',  #originally from sh_pos_customer_discount
    ],
}
