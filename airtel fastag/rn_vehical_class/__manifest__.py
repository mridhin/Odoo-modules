# -*- coding: utf-8 -*-
{
    'name': "Rdian Software",

    'summary': """
        Vehical Class For Fastag""",

    'description': """

    """,

    'author': "Redian Software",
    'website': "https://www.rediansoftware.com/",   

    'category': 'Inventory',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','account','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/rs_inv_group.xml',
        #'wizard/gt_add_product.xml',
	   'wizard/rs_import_fastag.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/rs_user_view.xml',
        'views/product.xml',
        'views/scheduled_action.xml',
        # 'views/invenotry_hide',
	    'views/transfer_report.xml',
        'data/email_template.xml',
        'reports/unacknowledged_tag_report.xml',

        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
