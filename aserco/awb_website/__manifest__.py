# -*- coding: utf-8 -*-
{
    'name': "AWB Website Landing Page",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'website': 'https://www.achievewithoutborders.com/',
    'author': 'Achieve Without Borders',
    'license': 'LGPL-3',
    'version': '15.0.1.0.0',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'website_blog'],

    # always loaded
    'data': [
        'views/blog_snippet_views.xml',
        'views/website_landin_page.xml',
        'views/calendar_appointment_type_views.xml',
        'views/footer_pages.xml'
    ],
    "assets": {
        'web.assets_frontend': [
            'awb_website/static/src/css/style.scss',
            'awb_website/static/src/js/website.js',
            'awb_website/static/src/js/email_chimp.js',
            'https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.2.1/owl.carousel.js',
            'awb_website/static/src/css/footer.scss',
            'awb_website/static/src/js/footer.js',
            'https://cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.min.js',
            'https://cdn.jsdelivr.net/gh/kenwheeler/slick@1.8.1/slick/slick-theme.css',
            'https://cdn.jsdelivr.net/npm/slick-carousel@1.8.1/slick/slick.css',
            'https://www.jqueryscript.net/css/jquerysctipttop.css',
            # 'https://code.jquery.com/jquery-3.4.1.slim.min.js',
            'awb_website/static/src/js/hip.js',
            'awb_website/static/src/js/myhip.js',
        ],
    },
}
