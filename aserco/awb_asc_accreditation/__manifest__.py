# -*- coding: utf-8 -*-

{
    'name': """AWB ASC accreditation""",
    'summary': '''AWB ASC accreditation''',
    'version': '15.0.1.0.0',
    'category': 'website',
    'summary': 'AWB ASC accreditation',
    'website': 'https://www.achievewithoutborders.com/',
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',
    'description': """
       AWB ASC accreditation
    """,
    'depends': ['website','contacts','awb_contact_extension'],

    'data': [
         'security/ir.model.access.csv',
          'data/awb_ecommerce.xml',
          'views/ecommerce_view.xml',
          'views/res_partner_views.xml'
          # 'views/asc_form.xml',
        
    ],
    'assets':{
            'web.assets_frontend': [
                'awb_asc_accreditation/static/scss/asc_form_design.scss',
                'awb_asc_accreditation/static/scss/chosen.min.css',
                'awb_asc_accreditation/static/src/js/asc.js',
                'awb_asc_accreditation/static/src/js/chosen.jquery.min.js',
        ],
            'web.assets_qweb': [
                    
        ],
    },
    

    
    
    # 'currency': 'EUR',
     'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
