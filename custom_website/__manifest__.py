# -*- coding: utf-8 -*-
{
    'name': "Custom Loyalty",
    'summary': "Use discount coupons in different sales channels.",
    'description': """Integrate coupon mechanism in orders.""",
    'category': 'Sales',
    'version': '16.0.1.0.0',
    'depends': ['account', 'loyalty'],
    'data': [
        'views/loyalty_rule_views.xml',
    ],
    'demo': [
        
    ],
    'installable': True,
    'license': 'LGPL-3',
}