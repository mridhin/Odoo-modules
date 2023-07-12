{
    'name': 'Stock Transfer Report',
    'version': '1.0',
    'author': 'Redian Services Pvt. Ltd.',
    'website': 'www.redian.com',
    'category': 'Sale',
    'sequence': 1,
    'depends': ['stock','rn_vehical_class'],
    'description': """
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/all_transfer_report.xml',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
    'application': True,
}
